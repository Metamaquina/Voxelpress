using Gee;




namespace voxelcore {
	private class ThreadTracker {
		private unowned Thread<void*> thread;
		public ThreadTracker(Thread<void*> t) {
			thread = t;
		}
		public void join() {
			thread.join();
		}
	}
	
	public class WorkerPool<SomeType> {
		private Mutex mutex = new Mutex();
		private AsyncQueue<SomeType> input_queue {get; set;}
		private LinkedList<ThreadTracker> pool {get; set;}
		public bool running {get; private set; default = false;}
		public bool dry_up {get; private set; default = false;}
		
		public signal void event_hook ( SomeType entity );
		
		public WorkerPool(AsyncQueue<SomeType?> work_src, int thread_count, bool wait) {
			pool = new LinkedList<ThreadTracker>();
			input_queue = work_src;
			if (wait) {
				mutex.lock();
			}
			else {
				running = true;
			}
			increase_pool(thread_count);
		}

		public void increase_pool(int n) requires(n > 0) {
			for (int i=0; i<n; i+=1) {
				unowned Thread<void*> foo = Thread.create<void*>(run_thread, true);
				foo.set_priority(ThreadPriority.HIGH);
				pool.add(new ThreadTracker(foo));
			}
		}
		
		public void start() {
			if (!running) {
				running = true;
				mutex.unlock();
			}
		}
		
		public void join_all () {
			dry_up = true;
			foreach (var thread in pool) {
				thread.join();
			}
		}
		
		public void* run_thread () {
			// Wait until start has been called:
			mutex.lock();
			mutex.unlock();
			
			while (true) {
				var wait = TimeVal();
				wait.add(1000);
				SomeType? datum = input_queue.timed_pop(ref wait);
				if (datum == null) {
					// queue was empty
					if (dry_up) {
						break;
					}
					else {
						//stdout.printf("thread stalled\n");
						Thread.yield();
						continue;
					}
				}
				else {
					// queue was not empty
					event_hook(datum);
				}
				Thread.yield();
			}
			return null;
		}
	}
}