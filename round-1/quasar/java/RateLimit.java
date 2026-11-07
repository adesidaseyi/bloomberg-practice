import java.util.*;
import java.util.function.DoubleSupplier;
public class RateLimit {
    static class Window { double start; int count; Window(double s,int c){start=s;count=c;} }
    private final int limit; private final double window; private final DoubleSupplier clock;
    private final Map<String,Window> state=new HashMap<>();
    public RateLimit(int limit,double window,DoubleSupplier clock){ this.limit=limit; this.window=window; this.clock=clock; }
    public boolean allow(String key){
        double now=clock.getAsDouble(); Window w=state.get(key);
        if(w==null){ w=new Window(now,0); state.put(key,w); }
        w.count++;
        if(w.count<=limit) return true;
        return false;
    }
    public int remaining(String key){
        Window w=state.get(key);
        if(w==null) return 0;
        return limit - w.count;
    }
    public void reset(String key){
    }
}
