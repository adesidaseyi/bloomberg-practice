#pragma once
#include <string>
#include <functional>
#include <stdexcept>
#include <chrono>
#include <utility>

enum class BreakerState { CLOSED, OPEN, HALF_OPEN };

class CircuitBreaker {
    int threshold_;
    double cooldown_;
    std::function<double()> clock_;
    BreakerState state_ = BreakerState::CLOSED;
    int failures_ = 0;
    double opened_at_ = 0.0;
    int probes_ = 0;
public:
    explicit CircuitBreaker(int failure_threshold = 3, double cooldown_seconds = 30.0,
                            std::function<double()> clock = nullptr)
        : threshold_(failure_threshold), cooldown_(cooldown_seconds), clock_(std::move(clock)) {
        if (threshold_ <= 0) throw std::invalid_argument("failure_threshold must be positive");
        if (cooldown_ < 0) throw std::invalid_argument("cooldown_seconds must be non-negative");
        if (!clock_) clock_ = [] {
            return std::chrono::duration<double>(
                std::chrono::steady_clock::now().time_since_epoch()).count();
        };
    }

    bool allow() {
        refresh();
        if (state_ == BreakerState::OPEN) return false;
        if (state_ == BreakerState::HALF_OPEN) return true;
        return true;
    }

    void record_success() {
        if (state_ == BreakerState::HALF_OPEN) {
            state_ = BreakerState::CLOSED;
            opened_at_ = 0.0;
            failures_ = 0;
        }
        probes_ = 0;
    }

    void record_failure() {
        if (state_ == BreakerState::HALF_OPEN) {
            state_ = BreakerState::OPEN;
            opened_at_ = clock_();
            probes_ = 0;
            return;
        }
        if (state_ == BreakerState::OPEN) return;
        ++failures_;
        if (failures_ >= threshold_) {
            state_ = BreakerState::OPEN;
            opened_at_ = clock_();
        }
    }

    BreakerState state() {
        refresh();
        return state_;
    }

    int failure_count() const { return failures_; }

    void reset() {
        state_ = BreakerState::CLOSED;
        opened_at_ = 0.0;
        probes_ = 0;
    }

private:
    void refresh() {
        if (state_ == BreakerState::OPEN && clock_() - opened_at_ >= cooldown_) {
            state_ = BreakerState::HALF_OPEN;
            probes_ = 0;
        }
    }
};
