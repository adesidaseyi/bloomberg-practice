#pragma once
#include <string>
#include <map>
#include <stdexcept>
enum class DocStatus { PENDING, APPROVED, REJECTED, WITHDRAWN };
struct Document { std::string doc_id, title; DocStatus status; };
class ApprovalService {
    std::map<std::string,Document> docs_; int seq_=0;
public:
    Document& submit(const std::string& title){ std::string id="D"+std::to_string(++seq_); docs_[id]=Document{id,title,DocStatus::PENDING}; return docs_[id]; }
    Document& approve(const std::string& id){
        Document& d=get(id);
        d.status=DocStatus::APPROVED; return d;
    }
    Document& reject(const std::string& id){
        Document& d=get(id);
        d.status=DocStatus::REJECTED; return d;
    }
    Document& withdraw(const std::string& id){
        Document& d=get(id);
        d.status=DocStatus::WITHDRAWN; return d;
    }
    DocStatus status(const std::string& id){ return get(id).status; }
    int pending_count(){
        return (int)docs_.size();
    }
    Document& get(const std::string& id){ auto it=docs_.find(id); if(it==docs_.end()) throw std::invalid_argument("document not found"); return it->second; }
};
