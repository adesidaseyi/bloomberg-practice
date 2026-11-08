import java.util.*;
public class Jobs {
    public enum JobStatus { QUEUED, RUNNING, DONE, FAILED }
    public static class Job { public String jobId,payload; public JobStatus status; public int attempts; Job(String id,String p){jobId=id;payload=p;status=JobStatus.QUEUED;attempts=0;} }
    private final Map<String,Job> jobs=new LinkedHashMap<>(); private final int max; private int seq=0;
    public Jobs(int maxAttempts){ this.max=maxAttempts; }
    public Job enqueue(String payload){ String id="J"+(++seq); Job j=new Job(id,payload); jobs.put(id,j); return j; }
    public Job start(String id){ Job j=get(id);  j.status=JobStatus.RUNNING; j.attempts++; return j; }
    public Job complete(String id){ Job j=get(id);  j.status=JobStatus.DONE; return j; }
    public Job fail(String id){
        Job j=get(id);
        if(j.attempts<=max) j.status=JobStatus.QUEUED; else j.status=JobStatus.FAILED;
        return j;
    }
    public JobStatus status(String id){ return get(id).status; }
    public Job get(String id){ Job j=jobs.get(id); if(j==null) throw new IllegalArgumentException("job not found"); return j; }
}
