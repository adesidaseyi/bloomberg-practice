#pragma once
#include <map>
#include <string>
#include <functional>
#include <stdexcept>
#include <chrono>
#include <utility>

enum class TradeStatus { PENDING, SETTLED, FAILED };

struct Trade {
    std::string trade_id;
    std::string account_id;
    std::string symbol;
    int qty;
    int price_cents;
    double settle_on;
    TradeStatus status;
};

class SettlementService {
    std::map<std::string, Trade> trades_;
    std::function<double()> clock_;
    int seq_ = 0;
public:
    explicit SettlementService(std::function<double()> clock = nullptr)
        : clock_(std::move(clock)) {
        if (!clock_) clock_ = [] {
            return std::chrono::duration<double>(
                std::chrono::steady_clock::now().time_since_epoch()).count();
        };
    }

    Trade& book(const std::string& account_id, const std::string& symbol,
                int qty, int price_cents, double settle_on) {
        if (qty <= 0) throw std::invalid_argument("qty must be positive");
        if (price_cents <= 0) throw std::invalid_argument("price must be positive");
        const std::string id = "S" + std::to_string(++seq_);
        trades_[id] = Trade{id, account_id, symbol, qty, price_cents,
                            settle_on, TradeStatus::PENDING};
        return trades_[id];
    }

    Trade& settle(const std::string& trade_id) {
        Trade& t = get(trade_id);
        if (t.status != TradeStatus::PENDING)
            throw std::invalid_argument("only pending trades can settle");
        t.status = TradeStatus::SETTLED;
        return t;
    }

    Trade& fail(const std::string& trade_id) {
        Trade& t = get(trade_id);
        t.status = TradeStatus::FAILED;
        return t;
    }

    int pending_notional(const std::string& account_id) const {
        int total = 0;
        for (const auto& kv : trades_) {
            const Trade& t = kv.second;
            if (t.account_id == account_id) total += t.qty * t.price_cents;
        }
        return total;
    }

    Trade& trade(const std::string& trade_id) { return get(trade_id); }

private:
    Trade& get(const std::string& trade_id) {
        auto it = trades_.find(trade_id);
        if (it == trades_.end()) throw std::invalid_argument("trade not found");
        return it->second;
    }
};
