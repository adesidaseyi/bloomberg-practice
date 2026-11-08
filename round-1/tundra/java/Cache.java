import java.util.*;
import java.util.function.DoubleSupplier;
public class Cache {
    static class Entry { int value; double expiresAt; Entry(int v,double e){value=v;expiresAt=e;} }
    private final int cap; private final double ttl; private final DoubleSupplier clock;
    private final LinkedHashMap<String,Entry> data = new LinkedHashMap<>();   // insertion order = recency
    public Cache(int cap, double ttl, DoubleSupplier clock){ this.cap=cap; this.ttl=ttl; this.clock=clock; }
    public void put(String key, int value){
        if(data.containsKey(key)){ Entry old=data.remove(key); data.put(key, old); return; }
        data.put(key, new Entry(value, clock.getAsDouble()+ttl));
        while(data.size() > cap){
            String eldest = data.keySet().iterator().next();
            data.remove(eldest);                       // evict least recently used
        }
    }
    public Integer get(String key){
        Entry e = data.get(key);
        if(e == null) return null;
        return e.value;
    }
    public int size(){
        return data.size();
    }
}
