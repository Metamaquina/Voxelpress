

namespace libvoxelpress.etc {
	public interface BPart : Object {
		public abstract void on_bubble(Object pushed, Object next);
	}

    public class BTree<Key,Val> : Object {
        public static delegate Object? creation_func ();
        public static delegate int cmp_func<Kind> (Kind lhs, Kind rhs);


        public class Capsule<Key,Val> : Object {
            public Key key;
            public Val? value { get; set; }
            public cmp_func<Key> _cmp { get; private set; }
            public Capsule (Key key, Val value, cmp_func<Key> cmp) {
                this._cmp = cmp;
                this.key = key;
                this.value = value;
            }
            public int cmp ( Capsule<Key,Val> rhs ) {
                return this._cmp(this.key, rhs.key);
            }
        }
 

        public class BNode<Key,Val> : Object, BPart {
            public weak BPart parent;
            public BNode<Key,Val>? lhs = null;
            public BNode<Key,Val>? mid = null;
            public BNode<Key,Val>? rhs = null;
            public bool is_root = false;
            public Capsule<Key,Val>? low = null;
            public Capsule<Key,Val>? high = null;
			public bool low_mask = false;
			public bool high_mask = false;

            public cmp_func<Key> cmp { get; set; }
            public creation_func on_create { get; set; }
            
            public bool full { get { return low_mask && high_mask; } }
            public int height { get; private set; }
            public bool is_bottom { get { return height == 1; } }

            public BNode ( int height, BPart parent, cmp_func<Key> cmp, creation_func on_create ) {
                this.height = height;
                this.parent = parent;
                this.cmp = cmp;
                this.on_create = on_create;
            }

            public BNode.seed ( BPart parent, cmp_func<Key> cmp, creation_func on_create ) {
                this.parent = (BPart) parent;
                this.cmp = cmp;
                this.on_create = on_create;
                is_root = true;
                height = 1;
            }

            public BNode<Key,Val>? route(Key key, bool no_create) {
                BNode<Key,Val>? result = null;
                if (low_mask) {
                    if (cmp(key, low.key) < 0) {
                        result = lhs;
                    }
                    else if (high_mask && cmp(key,high.key) > 0) {
                        if (!is_bottom && !no_create && rhs == null) {
                            rhs = new BNode<Key,Val>(height-1, this, cmp, on_create);
                        }
                        result = rhs;
                    }
                    else {
                        if (!is_bottom && !no_create && mid == null) {
                            mid = new BNode<Key,Val>(height-1, this, cmp, on_create);
                        }
                        result = mid;
                    }
                }
                return result;
            }

            public Capsule<Key,Val> encapsulate (Key key) {
                Val value = (Val) on_create();
                return new Capsule<Key,Val>(key, value, cmp);
            }

            public Val? pull_value(Key key) {
                if (low_mask && cmp(low.key, key) == 0) {
                    return low.value;
                }
                else if (high_mask && cmp(high.key, key) == 0) {
                    return high.value;
                }
                else {
                    return null;
                }
            }

			public bool contains(Capsule<Key,Val> cap) {
				return (low_mask && cap.key == low.key) || (high_mask && cap.key == high.key);
			}

            public bool push(Capsule<Key,Val> cap) {
                if (!contains(cap)) {
                    if (!is_bottom) {
                        var path = route(cap.key, false);
                        if (path != null) {
                            return path.push(cap);
                        }
                    }
                    else {
                        if (full) {
                            split(cap);
                        }
                        else {
                            // not full, so low might be null, but high absolutely is
                            if (!low_mask) {
                                low = cap;
								low_mask = true;
                            }
                            else {
                                if (cap.cmp(low) < 0) {
                                    high = low;
                                    low = cap;
                                }
                                else {
                                    high = cap;
                                }
								high_mask = true;
                            }
                        }
                        return true;
                    }
                }
				var test = pull_value(cap.key);
                return false;
            }
        
            public Val? fetch (Key key) {
                Val? found = pull_value(key);
                if (found != null) {
                    return found;
                }
                else if (!is_bottom) {
                    var path = route(key, true);
                    if (path != null) {
                        return path.fetch(key);
                    }
                }
                return null;
            }

            public Val? fetch_or_create(Key key) {
                Val? found = pull_value(key);
                if (found != null) {
                    return found;
                }
                else if (!is_bottom) {
                    var path = route(key, true);
                    if (path != null) {
                        return path.fetch_or_create(key);
                    }
                }
                // key not found, so create it and return it.
                var cap = encapsulate(key);
                push(cap);
				return cap.value;
            }

            public void on_bubble(Object _pushed, Object _next) {
				Capsule<Key,Val> pushed = (Capsule<Key,Val>) _pushed;
				BNode<Key,Val> next = (BNode<Key,Val>) _next;
                if (!full) {
                    if (pushed.cmp(low) < 0) {
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
                    var cascade = new BNode<Key,Val>(height, parent, cmp, on_create);
                    Capsule<Key,Val> bumped;
                    if (pushed.cmp(low) < 0) {
                        // push came from lhs
                        cascade.mid = rhs;
                        cascade.lhs = mid;
                        mid = next;
                        cascade.low = high;
                        bumped = low;
                        low = pushed;
                    }
                    else if (pushed.cmp(high) < 0) {
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
                    var displaced = new BNode<Key,Val>[] { cascade.lhs, cascade.mid, cascade.rhs };
                    foreach (BNode<Key,Val> node in displaced) {
                        if (node != null) {
                            node.parent = cascade;
                        }
                    }
                    parent.on_bubble(bumped, cascade);
                }
            }

            public void split(Capsule<Key,Val> cap) {
                var next = new BNode<Key,Val>(height, parent, cmp, on_create);
                Capsule<Key,Val> pushed;
                if (this.low.cmp(cap) > 0) {
					// low > cap
                    pushed = this.low;
                    this.low = cap;
                    next.low = this.high;
					this.high = null;
                }
                else if (this.high.cmp(cap) < 0) {
					// high < cap
                    pushed = this.high;
                    next.low = cap;
					this.high = null;
                }
                else {
                    pushed = cap;
                    next.low = this.high;
					this.high = null;
                }
				next.low_mask = true;
				high_mask = false;
                parent.on_bubble(pushed, next);
            }
        }



        
        public class BTreeHead<Key,Val> : Object, BPart {
            public BNode<Key,Val> root;
            public int depth { get { return root.height; } }
            public int size { get; private set; default = 0; }
            public cmp_func<Key> cmp { get; set; }
            public creation_func on_create { get; set; }

            public BTreeHead ( cmp_func<Key> cmp, creation_func on_create ) {
                this.cmp = cmp;
                this.on_create = on_create;
                root = new BNode<Key,Val>.seed(this, cmp, on_create);
            }

			public void push(Capsule cap) {
				size += root.push(cap) ? 1: 0;
			}

            public void on_bubble(Object _pushed, Object _next) {
				Capsule<Key,Val> pushed = (Capsule<Key,Val>) _pushed;
				BNode<Key,Val> next = (BNode<Key,Val>) _next;
				var top = new BNode<Key,Val>(root.height+1, (BPart)this, cmp, on_create);
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
        }


        public BTreeHead<Key,Val> head;
		public int size { get { return head.size; } }

        public BTree(cmp_func<Key> cmp, creation_func on_create ) {
            head = new BTreeHead<Key,Val>(cmp, on_create);
        }
		
		public Val? fetch(Key key) {
			return head.root.fetch(key);
		}
		
		public Val? fetch_or_create(Key key) {
			return head.root.fetch_or_create(key);
		}
		
		public void push(Key key, Val value) {
			Capsule<Key,Val> cap = new Capsule<Key,Val>(key, value, head.cmp);
			head.push(cap);
		}
    }
}
