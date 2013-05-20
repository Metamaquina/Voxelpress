

namespace libvoxelpress.etc {

    public delegate int BTreeComparisonFunction<SomeType> (SomeType x, SomeType y);
    public delegate void BTreeTransversalCallback<SomeType> (BNode<SomeType> node);
    public delegate void BTreeIterativeCallback<SomeType> (SomeType val);
    public delegate void BTreeShellCallback (int shell);
    
    
    public interface BTreePart<SomeType> : GLib.Object {
        public abstract void on_bubble(SomeType pushed, BNode<SomeType> next);
    }
    
    
    public class BNode<SomeType> : GLib.Object, BTreePart<SomeType> {
        public weak BTreePart<SomeType> parent;
        public BNode<SomeType>? lhs = null;
        public BNode<SomeType>? mid = null;
        public BNode<SomeType>? rhs = null;
        public bool full { get { return low_mask && high_mask; } }
        public bool is_root = false;
        public int height { get; private set; }
        public bool bottom { get { return height == 1; } }
        public SomeType low;
        public SomeType high;
        public bool low_mask = false;
        public bool high_mask = false;
        
        private BTreeComparisonFunction<SomeType> cmp {get; set;}
        
        public BNode(int height, BTreePart<SomeType> parent, BTreeComparisonFunction<SomeType> cmp) {
            this.parent = parent;
            this.height = height;
            this.cmp = cmp;
        }
        public BNode.seed(BTree<SomeType> parent, BTreeComparisonFunction<SomeType> cmp) {
            this.parent = (BTreePart) parent;
            this.cmp = cmp;
            is_root = true;
            height = 1;
        }
        
        private BNode<SomeType>? route(SomeType val, bool no_create) {
            BNode<SomeType>? result = null;
            if (low_mask) {
                if (cmp(val, low) < 0) {
                    result = lhs;
                }
                else if (high_mask && cmp(val, high) > 0) {
                    if (!bottom && !no_create && rhs == null) {
                        rhs = new BNode<SomeType>(height-1, this, cmp);
                    }
                    result = rhs;
                }
                else {
                    if (!bottom && !no_create && mid == null) {
                        mid = new BNode<SomeType>(height-1, this, cmp);
                    }
                    result = mid;
                }
            }
            return result;
        }
        
        public void sequential(BTreeIterativeCallback<SomeType> func) {
            if (!bottom && lhs != null) {
                lhs.sequential(func);
            }
            if (low_mask) {
                func(low);
            }
            if (!bottom && mid != null) {
                mid.sequential(func);
            }
            if (high_mask) {
                func(high);
            }
            if (!bottom && rhs != null) {
                rhs.sequential(func);
            }
        }
        
        public void breadth_first(BTreeTransversalCallback<SomeType> func, int target) {
            if (bottom || (height == target)) {
                func(this);
            }
            else if(!bottom) {
                if (lhs != null) {
                    lhs.breadth_first(func, target);
                }
                if (mid != null) {
                    mid.breadth_first(func, target);
                }
                if (rhs != null) {
                    rhs.breadth_first(func, target);
                }
            }
        }
        
        private bool contains(SomeType val) {
            return (low_mask && cmp(val, low) == 0) || (high_mask && cmp(val, high) == 0);
        }

		public SomeType? fetch(SomeType val) {
			if (contains(val)) {
				return cmp(val, low) == 0 ? low : high;
			}
			else if (!bottom) {
				var path = route(val, true);
				if (path != null) {
					return path.fetch(val);
				}
			}
			return null;
		}
        
        public bool push(SomeType val) {
            if (!contains(val)) {
                if (!bottom) {
                    var path = route(val, false);
                    if (path != null) {
                        return path.push(val);
                    }
                }
                else {
                    if (full) {
                        split(val);
                    }
                    else {
                        // not full, so low might be null, but high absolutely is
                        if (!low_mask) {
                            low = val;
                            low_mask = true;
                        }
                        else {
                            if (cmp(val, low) < 0) {
                                high = low;
                                low = val;
                            }
                            else {
                                high = val;
                            }
                            high_mask = true;
                        }
                    }
                    return true;
                }
            }
            return false;
        }
        
        public void on_bubble(SomeType pushed, BNode<SomeType> next) {
            if (!full) {
                if (cmp(pushed,low) < 0) {
                    high = low;
                    low = pushed;
                    high_mask = true;
                    if (mid != null) {
                        rhs = mid;
                    }
                    mid = next;
                }
                else {
                    high = pushed;
                    rhs = next;
                    high_mask = true;
                }
            }
            else {
                var cascade = new BNode<SomeType>(height, parent, cmp);
                SomeType bumped;
                if (cmp(pushed,low) < 0) {
                    // push came from lhs
                    cascade.mid = rhs;
                    cascade.lhs = mid;
                    mid = next;
                    cascade.low = high;
                    bumped = low;
                    low = pushed;
                }
                else if (cmp(pushed, high) < 0) {
                    // push came from mid
                    cascade.mid = rhs;
                    cascade.lhs = next;
                    cascade.low = high;
                    bumped = pushed;
                }
                else {
                    // push came from rhs
                    cascade.mid = next;
                    cascade.lhs = rhs;
                    cascade.low = pushed;
                    bumped = high;
                }
                cascade.low_mask = true;
                cascade.high_mask = false;
                low_mask = true;
                high_mask = false;
                rhs = null;
                var displaced = new BNode<SomeType>[] { cascade.lhs, cascade.mid, cascade.rhs };
                foreach (BNode<SomeType> node in displaced) {
                    if (node != null) {
                        node.parent = cascade;
                    }
                }
                parent.on_bubble(bumped, cascade);
            }
        }
        
        private void split(SomeType val) {
            var next = new BNode<SomeType>(height, parent, cmp);
            SomeType pushed;
            if (cmp(this.low, val) > 0) {
                pushed = this.low;
                this.low = val;
                next.low = this.high;
            }
            else if (cmp(this.high, val) < 0) {
                pushed = this.high;
                next.low = val;
            }
            else {
                pushed = val;
                next.low = this.high;
            }
            next.low_mask = true;
            high_mask = false;
            parent.on_bubble(pushed, next);
        }
    }
    
    
    public class BTree<SomeType> : GLib.Object, BTreePart<SomeType> {
        private BNode<SomeType> root;
        private BTreeComparisonFunction<SomeType> cmp {get; set;}
        public int depth { get { return root.height; } }
        public int size { get; private set; default = 0; }
        
        public BTree (BTreeComparisonFunction cmp) {
            this.cmp = cmp;
            root = new BNode<SomeType>.seed(this, cmp);
        }

		public SomeType? fetch(SomeType val) {
			return root.fetch(val);
		}
        
        public bool has(SomeType val) {
			return root.fetch(val) != null;
        }
        
        public void push(SomeType val) {
            size += root.push(val) ? 1 : 0;
        }
        
        public void on_bubble(SomeType pushed, BNode<SomeType> next) {
            var top = new BNode<SomeType>(root.height+1, (BTreePart)this, cmp);
            top.is_root = true;
            top.lhs = root;
            top.low = pushed;
            top.low_mask = true;
            top.high_mask = false;
            top.mid = next;
            next.parent = top;
            root.parent = top;
            root.is_root = false;
            root = top;
        }
        
        public void sequential (BTreeIterativeCallback<SomeType> func) {
            // Calls 'func' on all tree elements, in order from lowest to highest.
            root.sequential(func);
        }
        
        public void breadth_first (BTreeTransversalCallback<SomeType> func, BTreeShellCallback on_shell) {
            // Calls 'func' on all tree elements, via breadth first transversal.
			// Calls 'on_shell' at the beginning of each 'shell' of the b-tree.
            for (int shell = root.height; shell>=1; shell-=1) {
                on_shell(root.height-shell+1);
                root.breadth_first(func, shell);
            }
        }
    }
}