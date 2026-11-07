#pragma once
#include <string>
#include <map>
#include <functional>
#include <stdexcept>
enum class SubStatus { TRIAL, ACTIVE, SUSPENDED, CANCELLED, EXPIRED };
struct Subscription { std::string sub_id, user_id; SubStatus status; double expires_at; bool has_expiry; };
class SubscriptionService {
    std::map<std::string,Subscription> subs_;
    double ttl_; std::function<double()> clock_; int seq_=0;
public:
    SubscriptionService(double ttl, std::function<double()> clock): ttl_(ttl), clock_(clock) {}
    Subscription& start_trial(const std::string& user){
        std::string id="S"+std::to_string(++seq_);
        subs_[id]=Subscription{id,user,SubStatus::TRIAL,clock_()+ttl_,true}; return subs_[id];
    }
    Subscription& activate(const std::string& id){
        Subscription& s=get(id);
        s.status=SubStatus::ACTIVE; s.has_expiry=false; return s;
    }
    Subscription& suspend(const std::string& id){
        Subscription& s=get(id);
        if(s.status!=SubStatus::ACTIVE && s.status!=SubStatus::TRIAL) throw std::invalid_argument("only active can be suspended");
        s.status=SubStatus::SUSPENDED; return s;
    }
    Subscription& resume(const std::string& id){
        Subscription& s=get(id);
        if(s.status!=SubStatus::SUSPENDED) throw std::invalid_argument("only suspended can be resumed");
        s.status=SubStatus::ACTIVE; return s;
    }
    Subscription& cancel(const std::string& id){
        Subscription& s=get(id);
        s.status=SubStatus::CANCELLED; s.has_expiry=false; return s;
    }
    bool is_entitled(const std::string& id){
        Subscription& s=get(id);
        if(s.status==SubStatus::ACTIVE) return true;
        if(s.status==SubStatus::SUSPENDED) return true;
        if(s.status==SubStatus::TRIAL) return true;
        return false;
    }
    Subscription& get(const std::string& id){ auto it=subs_.find(id); if(it==subs_.end()) throw std::invalid_argument("not found"); return it->second; }
private:
    void cleanup(){ double now=clock_(); for(auto& kv:subs_){ auto& s=kv.second; if(s.status==SubStatus::TRIAL && s.has_expiry && s.expires_at<=now) s.status=SubStatus::EXPIRED; } }
};
