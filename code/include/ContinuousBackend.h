#pragma once

#include "PPEBackend.h"
#include <eigen3/Eigen/Core>

class ContinuousBackend : public PPEBackend
{
public:
    void showState() override;
    Point *getActivePoint() const override;

private:
    void _addSuccessfulObservation(Point *point) override;
    void _addFailedObservation(Point *point) override;
};
