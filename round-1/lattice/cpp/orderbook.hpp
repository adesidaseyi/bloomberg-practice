#pragma once
#include <map>
#include <vector>
#include <string>
#include <stdexcept>
#include <optional>
#include <algorithm>

enum class Side { BUY, SELL };
enum class OrderStatus { OPEN, PARTIAL, FILLED, CANCELLED };

struct Order {
    std::string order_id;
    Side side;
    int price_cents;
    int qty;
    int remaining;
    OrderStatus status;
    int seq;
};

struct Trade {
    std::string trade_id;
    int price_cents;
    int qty;
    std::string buy_order_id;
    std::string sell_order_id;
};

class OrderBook {
    std::map<std::string, Order> orders_;
    std::map<std::string, Order*> bids_;
    std::map<std::string, Order*> asks_;
    int seq_ = 0;
    int trade_seq_ = 0;
public:
    std::vector<Trade> submit(const std::string& side, int price_cents, int qty) {
        Side s;
        if (side == "buy") s = Side::BUY;
        else if (side == "sell") s = Side::SELL;
        else throw std::invalid_argument("side must be buy or sell");
        if (price_cents <= 0) throw std::invalid_argument("price must be positive");
        if (qty <= 0) throw std::invalid_argument("qty must be positive");

        const std::string id = "O" + std::to_string(++seq_);
        orders_[id] = Order{id, s, price_cents, qty, qty, OrderStatus::OPEN, seq_};
        Order& incoming = orders_[id];
        std::vector<Trade> trades;

        Order* resting = best_opposite(s);
        if (resting != nullptr && crosses(incoming, *resting)) {
            const int level = resting->price_cents;
            while (incoming.remaining > 0) {
                resting = best_opposite(s);
                if (resting == nullptr || resting->price_cents != level) break;
                if (!crosses(incoming, *resting)) break;
                execute(incoming, *resting, trades);
            }
        }

        if (incoming.remaining == 0) {
            incoming.status = OrderStatus::FILLED;
        } else {
            if (incoming.remaining < incoming.qty) incoming.status = OrderStatus::PARTIAL;
            book(s)[id] = &incoming;
        }
        return trades;
    }

    Order& cancel(const std::string& order_id) {
        Order& o = order(order_id);
        if (o.status != OrderStatus::OPEN && o.status != OrderStatus::PARTIAL)
            throw std::invalid_argument("only open or partially filled orders can be cancelled");
        o.status = OrderStatus::CANCELLED;
        bids_.erase(order_id);
        asks_.erase(order_id);
        return o;
    }

    Order& order(const std::string& order_id) {
        auto it = orders_.find(order_id);
        if (it == orders_.end()) throw std::invalid_argument("order not found");
        return it->second;
    }

    std::optional<int> best_bid() const {
        std::optional<int> best;
        for (const auto& kv : bids_) {
            const int p = kv.second->price_cents;
            if (!best || p > *best) best = p;
        }
        return best;
    }

    std::optional<int> best_ask() const {
        std::optional<int> best;
        for (const auto& kv : asks_) {
            const int p = kv.second->price_cents;
            if (!best || p < *best) best = p;
        }
        return best;
    }

private:
    void execute(Order& incoming, Order& resting, std::vector<Trade>& trades) {
        const int take = std::min(incoming.remaining, resting.remaining);
        ++trade_seq_;
        const std::string buy_id = incoming.side == Side::BUY ? incoming.order_id : resting.order_id;
        const std::string sell_id = incoming.side == Side::BUY ? resting.order_id : incoming.order_id;
        trades.push_back(Trade{"T" + std::to_string(trade_seq_), incoming.price_cents,
                               take, buy_id, sell_id});
        incoming.remaining -= take;
        resting.remaining -= take;
        if (incoming.remaining == 0) incoming.status = OrderStatus::FILLED;
        else incoming.status = OrderStatus::PARTIAL;
        if (resting.remaining == 0) {
            resting.status = OrderStatus::FILLED;
            book(resting.side).erase(resting.order_id);
        } else {
            resting.status = OrderStatus::PARTIAL;
        }
    }

    Order* best_opposite(Side side) {
        auto& b = side == Side::BUY ? asks_ : bids_;
        if (b.empty()) return nullptr;
        Order* best = nullptr;
        for (auto& kv : b) {
            Order* o = kv.second;
            if (best == nullptr) { best = o; continue; }
            if (side == Side::BUY) {
                if (o->price_cents < best->price_cents ||
                    (o->price_cents == best->price_cents && o->seq > best->seq)) best = o;
            } else {
                if (o->price_cents > best->price_cents ||
                    (o->price_cents == best->price_cents && o->seq > best->seq)) best = o;
            }
        }
        return best;
    }

    static bool crosses(const Order& incoming, const Order& resting) {
        if (incoming.side == Side::BUY) return resting.price_cents <= incoming.price_cents;
        return resting.price_cents >= incoming.price_cents;
    }

    std::map<std::string, Order*>& book(Side side) {
        return side == Side::BUY ? bids_ : asks_;
    }
};
