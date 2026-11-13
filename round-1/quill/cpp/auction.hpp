#pragma once
#include <string>
#include <functional>
#include <stdexcept>
#include <chrono>
#include <utility>
#include <optional>

enum class AuctionStatus { OPEN, CLOSED };

struct Bid {
    std::string bid_id;
    std::string bidder_id;
    int amount_cents;
};

class AuctionService {
    int reserve_;
    double closes_at_;
    std::function<double()> clock_;
    AuctionStatus status_ = AuctionStatus::OPEN;
    std::optional<Bid> highest_;
    int seq_ = 0;
public:
    explicit AuctionService(int reserve_cents, double closes_at,
                            std::function<double()> clock = nullptr)
        : reserve_(reserve_cents), closes_at_(closes_at), clock_(std::move(clock)) {
        if (reserve_ < 0) throw std::invalid_argument("reserve must be non-negative");
        if (!clock_) clock_ = [] {
            return std::chrono::duration<double>(
                std::chrono::steady_clock::now().time_since_epoch()).count();
        };
    }

    Bid bid(const std::string& bidder_id, int cents) {
        if (cents <= 0) throw std::invalid_argument("bid amount must be positive");
        ++seq_;
        Bid b{"B" + std::to_string(seq_), bidder_id, cents};
        highest_ = b;
        return b;
    }

    AuctionStatus status() {
        refresh();
        return status_;
    }

    std::optional<Bid> highest_bid() const { return highest_; }

    std::optional<Bid> winner() {
        refresh();
        if (status_ == AuctionStatus::OPEN) return std::nullopt;
        return highest_;
    }

private:
    void refresh() {
        if (status_ == AuctionStatus::OPEN && clock_() >= closes_at_) {
            status_ = AuctionStatus::CLOSED;
        }
    }
};
