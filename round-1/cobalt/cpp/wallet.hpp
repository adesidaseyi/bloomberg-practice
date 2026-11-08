#pragma once
#include <string>
#include <map>
#include <stdexcept>
enum class HoldStatus { HELD, CAPTURED, VOIDED };
struct Hold { std::string hold_id, account_id; int amount; HoldStatus status; };
class WalletService {
    std::map<std::string,int> balance_;
    std::map<std::string,Hold> holds_;
    int seq_=0;
public:
    void open_account(const std::string& acct, int cents){ if(cents<0) throw std::invalid_argument("opening balance"); balance_[acct]=cents; }
    int balance(const std::string& acct){ return require(acct); }
    int available(const std::string& acct){
        int bal=require(acct);
        return bal-active_holds(acct);
    }
    Hold& authorize(const std::string& acct, int cents){
        require(acct);
        if(cents<=0) throw std::invalid_argument("amount must be positive");
        if(balance(acct)<cents) throw std::invalid_argument("insufficient available funds");
        std::string id="H"+std::to_string(++seq_);
        holds_[id]=Hold{id,acct,cents,HoldStatus::HELD}; return holds_[id];
    }
    Hold& capture(const std::string& id){
        Hold& h=get(id);
        h.status=HoldStatus::CAPTURED; return h;
    }
    Hold& voidHold(const std::string& id){
        Hold& h=get(id);
        h.status=HoldStatus::VOIDED; return h;
    }
    Hold& get(const std::string& id){ auto it=holds_.find(id); if(it==holds_.end()) throw std::invalid_argument("hold not found"); return it->second; }
private:
    int active_holds(const std::string& acct){ int s=0; for(auto& kv:holds_){ auto& h=kv.second; if(h.account_id==acct) s+=h.amount; } return s; }
    int require(const std::string& acct){ auto it=balance_.find(acct); if(it==balance_.end()) throw std::invalid_argument("unknown account"); return it->second; }
};
