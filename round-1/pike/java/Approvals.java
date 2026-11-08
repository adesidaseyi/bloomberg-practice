import java.util.*;
public class Approvals {
    public enum DocStatus { PENDING, APPROVED, REJECTED, WITHDRAWN }
    public static class Document { public String docId,title; public DocStatus status; Document(String id,String t){docId=id;title=t;status=DocStatus.PENDING;} }
    private final Map<String,Document> docs=new LinkedHashMap<>(); private int seq=0;
    public Document submit(String title){ String id="D"+(++seq); Document d=new Document(id,title); docs.put(id,d); return d; }
    public Document approve(String id){ Document d=get(id);  d.status=DocStatus.APPROVED; return d; }
    public Document reject(String id){ Document d=get(id);  d.status=DocStatus.REJECTED; return d; }
    public Document withdraw(String id){ Document d=get(id);  d.status=DocStatus.WITHDRAWN; return d; }
    public DocStatus status(String id){ return get(id).status; }
    public int pendingCount(){  return docs.size(); }
    public Document get(String id){ Document d=docs.get(id); if(d==null) throw new IllegalArgumentException("document not found"); return d; }
}
