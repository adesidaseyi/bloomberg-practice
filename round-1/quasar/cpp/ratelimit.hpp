#pragma once
#include <string>
#include <map>
#include <functional>
struct Window { double start; int count; };
class RateLimiter {
    int limit_; double window_; std::function<double()> clock_;
    std::map<std::string,Window> state_;
public:
    RateLimiter(int limit, double window, std::function<double()> clock): limit_(limit), window_(window), clock_(clock) {}
    bool allow(const std::string& key){
        double now=clock_();
        auto it=state_.find(key);
        if(it==state_.end()){ state_[key]=Window{now,0}; it=state_.find(key); }
        Window& w=it->second;
        w.count++;
        if(w.count<=limit_) return true;
        return false;
    }
    int remaining(const std::string& key){
        auto it=state_.find(key);
        if(it==state_.end()) return 0;
        return limit_ - it->second.count;
    }
    void reset(const std::string& key){
        (void)key;
    }
};
