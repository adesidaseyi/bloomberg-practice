import java.util.*;
import java.util.function.DoubleSupplier;
public class Subscriptions {
    public enum SubStatus { TRIAL, ACTIVE, SUSPENDED, CANCELLED, EXPIRED }
    public static class Subscription { public String subId,userId; public SubStatus status; double expiresAt; boolean hasExpiry;
        Subscription(String id,String u,double e){subId=id;userId=u;status=SubStatus.TRIAL;expiresAt=e;hasExpiry=true;} }
    private final Map<String,Subscription> subs=new LinkedHashMap<>();
    private final double ttl; private final DoubleSupplier clock; private int seq=0;
    public Subscriptions(double ttl, DoubleSupplier clock){ this.ttl=ttl; this.clock=clock; }
    public Subscription startTrial(String user){ String id="S"+(++seq); Subscription s=new Subscription(id,user,clock.getAsDouble()+ttl); subs.put(id,s); return s; }
    public Subscription activate(String id){
        Subscription s=get(id); s.status=SubStatus.ACTIVE; s.hasExpiry=false; return s;
    }
    public Subscription suspend(String id){ Subscription s=get(id); if(s.status!=SubStatus.ACTIVE && s.status!=SubStatus.TRIAL) throw new IllegalArgumentException("only active"); s.status=SubStatus.SUSPENDED; return s; }
    public Subscription resume(String id){ Subscription s=get(id); if(s.status!=SubStatus.SUSPENDED) throw new IllegalArgumentException("only suspended"); s.status=SubStatus.ACTIVE; return s; }
    public Subscription cancel(String id){
        Subscription s=get(id);
        s.status=SubStatus.CANCELLED; s.hasExpiry=false; return s;
    }
    public boolean isEntitled(String id){
        Subscription s=get(id);
        if(s.status==SubStatus.ACTIVE) return true;
        if(s.status==SubStatus.SUSPENDED) return true;
        if(s.status==SubStatus.TRIAL) return true;
        return false;
    }
    public Subscription get(String id){ Subscription s=subs.get(id); if(s==null) throw new IllegalArgumentException("not found"); return s; }
    private void cleanup(){ double now=clock.getAsDouble(); for(Subscription s: subs.values()) if(s.status==SubStatus.TRIAL && s.hasExpiry && s.expiresAt<=now) s.status=SubStatus.EXPIRED; }
}
