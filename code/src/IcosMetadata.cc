#include "IcosMetadata.h"
#include <algorithm>

void IcosMetadata::addFailedObservation(Eigen::Matrix4f observerPose, Eigen::Vector3f pointPose)
{
  float distance = (observerPose.block<3, 1>(0, 3) - pointPose).norm();
  int face = getClosestIcosFaceIndex(observerPose.block<3, 1>(0, 3));
  if (distance > faceDists[face])
    return;
  // Decrease p(seen | exists)
  faceWeights[face] = (1 - alpha) * faceWeights[face];

  // Use Bayes theorem to update pExists
  float pSeenGivenExists = faceWeights[face];
  float pNotSeenGivenExists = 1.0f - pSeenGivenExists;
  float pNotSeenGivenNotExists = 1.0f; // If it doesn't exist, it can't be seen
  float pExistsPrior = pExists;
  float pNotExistsPrior = 1.0f - pExistsPrior;

  // Bayes: p(exists|not seen) = [p(not seen|exists) * p(exists)] / p(not seen)
  float pNotSeen = pNotSeenGivenExists * pExistsPrior + pNotSeenGivenNotExists * pNotExistsPrior;
  if (pNotSeen > 0.0f)
    pExists = (pNotSeenGivenExists * pExistsPrior) / pNotSeen;
  else
    pExists = 0.0f;
  std::cout << pExists << std::endl;
}

void IcosMetadata::addSuccessfulObservation(Eigen::Matrix4f observerPose, Eigen::Vector3f pointPose)
{
  float distance = (observerPose.block<3, 1>(0, 3) - pointPose).norm();
  int face = getClosestIcosFaceIndex(observerPose.block<3, 1>(0, 3));
  faceDists[face] = std::max(faceDists[face], distance);

  // Increase P(seen | exists)
  faceWeights[face] = alpha + ((1 - alpha) * faceWeights[face]);
  pExists = 0.9;
  std::cout << pExists << std::endl;
}

int IcosMetadata::getClosestIcosFaceIndex(Eigen::Vector3f cameraPose)
{
  // Generate a vector from the point pose to the camera pose
  auto pointToCam = (pPoint->getPose() - cameraPose).normalized();
  float maxDot = -1.0f;
  int closestIdx = -1;
  for (size_t i = 0; i < faceCenterVecs.size(); ++i)
  {
    float dot = pointToCam.dot(faceCenterVecs[i]);
    if (dot > maxDot)
    {
      maxDot = dot;
      closestIdx = static_cast<int>(i);
    }
  }
  return closestIdx;
}