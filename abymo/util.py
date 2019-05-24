import os


def resolveRelativePath(base_path, rel_path):
  """Returns the absolute path for a link relative to base."""
  dirname = os.path.dirname(base_path)
  joined = os.path.join(dirname, rel_path)
  return os.path.normpath(joined)

# A note on plane transformations:
# A transformation t is applied to a point in the plane (x, y) to produce a
# new point (t[0]+t[2]*x, t[1]+t[2]*x). It can be shown that applying two
# transforms t1 and t0 in succession is equivalent to a single transform
# compose(t0, t1). It follows that the identity transform is [0,0,1] and that
# for any transform t we can compute a right inverse invert(t) such that
# compose(t, invert(t)) is the identity.

def compose(t0, t1):
  """Combine two plane transformations."""
  return [t0[0]+t0[2]*t1[0], t0[1]+t0[2]*t1[1], t0[2]*t1[2]]

def invert(t):
  """Invert a plane transformation (right inverse)."""
  return [-t[0]/t[2], -t[1]/t[2], 1/t[2]]

def zoom(z, transform, fixedPoint):
  """Zoom by applying a transform that increases scale around a fixed point."""
  zt = [(1-z)*fixedPoint[0], (1-z)*fixedPoint[1], z]
  return compose(zt, transform)



