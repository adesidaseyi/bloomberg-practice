import java.util.*;
public class Wallet {
    public enum HoldStatus { HELD, CAPTURED, VOIDED }
    public static class Hold { public String holdId,accountId; public int amount; public HoldStatus status;
        Hold(String id,String a,int amt){holdId=id;accountId=a;amount=amt;status=HoldStatus.HELD;} }
    private final Map<String,Integer> balance=new HashMap<>();
    private final Map<String,Hold> holds=new LinkedHashMap<>();
    private int seq=0;
    public void openAccount(String acct,int cents){ if(cents<0) throw new IllegalArgumentException("opening"); balance.put(acct,cents); }
    public int balance(String acct){ return require(acct); }
    public int available(String acct){
        int bal=require(acct);
        return bal-activeHolds(acct);
    }
    public Hold authorize(String acct,int cents){
        require(acct);
        if(cents<=0) throw new IllegalArgumentException("amount");
        if(balance(acct)<cents) throw new IllegalArgumentException("insufficient");
        String id="H"+(++seq); Hold h=new Hold(id,acct,cents); holds.put(id,h); return h;
    }
    public Hold capture(String id){
        Hold h=get(id);
        h.status=HoldStatus.CAPTURED; return h;
    }
    public Hold voidHold(String id){
        Hold h=get(id);
        h.status=HoldStatus.VOIDED; return h;
    }
    public Hold get(String id){ Hold h=holds.get(id); if(h==null) throw new IllegalArgumentException("hold not found"); return h; }
    private int activeHolds(String acct){ int s=0; for(Hold h: holds.values()) if(h.accountId.equals(acct)) s+=h.amount; return s; }
    private int require(String acct){ Integer b=balance.get(acct); if(b==null) throw new IllegalArgumentException("unknown account"); return b; }
}
