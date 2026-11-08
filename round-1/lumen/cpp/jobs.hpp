#pragma once
#include <string>
#include <map>
#include <stdexcept>
enum class JobStatus { QUEUED, RUNNING, DONE, FAILED };
struct Job { std::string job_id, payload; JobStatus status; int attempts; };
class JobQueue {
    std::map<std::string,Job> jobs_; int max_; int seq_=0;
public:
    explicit JobQueue(int max_attempts=2): max_(max_attempts) {}
    Job& enqueue(const std::string& payload){ std::string id="J"+std::to_string(++seq_); jobs_[id]=Job{id,payload,JobStatus::QUEUED,0}; return jobs_[id]; }
    Job& start(const std::string& id){
        Job& j=get(id);
        j.status=JobStatus::RUNNING; j.attempts++; return j;
    }
    Job& complete(const std::string& id){
        Job& j=get(id);
        j.status=JobStatus::DONE; return j;
    }
    Job& fail(const std::string& id){
        Job& j=get(id);
        if(j.attempts<=max_) j.status=JobStatus::QUEUED; else j.status=JobStatus::FAILED;
        return j;
    }
    JobStatus status(const std::string& id){ return get(id).status; }
    Job& get(const std::string& id){ auto it=jobs_.find(id); if(it==jobs_.end()) throw std::invalid_argument("job not found"); return it->second; }
};
