#include <vector>
#include <Eigen/Core>

class DiscreteBoundary
{
private:
    int n;
    std::vector<Eigen::Vector3f> face_centers;

public:
    DiscreteBoundary(int n);

private:
    void generateFaceCenters(int n);
    int getBinIndex(const Eigen::Vector3f &viewpoint);
};