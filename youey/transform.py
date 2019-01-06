import numpy as np
import math
from types import SimpleNamespace

class Transform:
  
  identity = [
    [1., 0., 0., 0.],
    [0., 1., 0., 0.],
    [0., 0., 1., 0.],
    [0., 0., 0., 1.]
  ]
  
  def __init__(self):
    self.matrix = np.array(self.identity)
    
    self.rotation = 0.
    self.rotation_x = 0.
    self.rotation_y = 0.
    self.rotation_z = 0.
    self.scale = 1.
    self.scale_x = 1.
    self.scale_y = 1.
    self.scale_z = 1.
    self.skew = 0.
    self.skew_x = 0.
    self.skew_y = 0.
    self.translate=(0., 0., 0.)
    self.translate_x = 0.
    self.translate_y = 0.
    self.translate_z = 0.

  @staticmethod
  def combine(a, b, ascl, bscl):
    result = []
    result.append(ascl * a[0] + bscl * b[0])
    result.append(ascl * a[1] + bscl * b[1])
    if len(a) == 3 and len(b) == 3:
      result.append(ascl * a[2] + bscl * b[2])
    return np.array(result)
    
  def unmatrix(self):
    '''
    Returns an object containing the matrix
    decomposed into transform operations, or
    None if the matrix cannot be decomposed.
    '''
    
    matrix = self.matrix
    
    if matrix[3][3] == 0: return None
    
    #Normalize
    matrix /= matrix[3][3]
  
    #perspective_matrix = matrix.copy()
    #for i in range(3):
      #perspective_matrix[i][3] = 0
    #perspective_matrix[3][3] = 1
    
    '''
    if np.linalg.det(perspective_matrix) == 0:
      print('det is 0')
      return None
    '''
    
    if matrix[0][3] != 0 or matrix[1][3] != 0 or matrix[2][3] != 0:
      matrix[0][3] = matrix[1][3] = matrix[2][3] = 0
      matrix[3][3] = 1
      
    translateX = matrix[3][0];
    translateY = matrix[3][1];
    translateZ = matrix[3][2];
  
    row = np.zeros((3, 3))
    for i in range(3):
      row[i] = matrix[i][:3]
    
    scaleX = np.sqrt(row[0].dot(row[0])) # magnitude
    row[0] = row[0]/scaleX # unit vector
    
    skew = np.dot(row[0], row[1])
    row[1] = Transform.combine(row[1], row[0], 1.0, -skew)
    
    scaleY = np.sqrt(row[1].dot(row[1])) # magnitude
    row[1] = row[1]/scaleY # unit vector
    skew /= scaleY
    
    skewX = np.dot(row[0], row[2])
    row[2] = Transform.combine(row[2], row[0], 1.0, -skewX)
    skewY = np.dot(row[1], row[2])
    row[2] = Transform.combine(row[2], row[1], 1.0, -skewY)
    
    scaleZ = np.sqrt(row[2].dot(row[2])) # magnitude
    row[2] /= scaleZ
    skewX /= scaleZ
    skewY /= scaleZ
    
    pdum3 = np.cross(row[1], row[2])
    if np.dot(row[0], pdum3) < 0:
      scaleX *= -1
      row *= -1
        
    rotateY = math.asin(-row[0][2])
    if math.cos(rotateY) != 0:
      rotateX = math.atan2(row[1][2], row[2][2])
      rotateZ = math.atan2(row[0][1], row[0][0])
    else:
      rotateX = math.atan2(-row[2][0], row[1][1])
      rotateZ = 0
    
    self.rotation = math.degrees(rotateZ)
    self.rotation_x = math.degrees(rotateX)
    self.rotation_y = math.degrees(rotateY)
    self.rotation_z = math.degrees(rotateZ)
    self.scale = scaleX if scaleX == scaleY else None
    self.scale_x = scaleX
    self.scale_y = scaleY
    self.scale_z = scaleZ
    self.skew = math.degrees(skew)
    self.skew_x = math.degrees(skewX)
    self.skew_y = math.degrees(skewY)
    self.translate = (translateX, translateY, translateZ)
    self.translate_x = translateX
    self.translate_y = translateY
    self.translate_z = translateZ

  def from_css(self, css):
    is3d = css.startswith('matrix3d')
    numbers = css[css.index('(')+1:css.index(')')]
    values = [float(value) for value in numbers.split(',')]
    
    if css.startswith('matrix3d'):
      self.matrix = np.array([
        [values[0], values[1], values[2], values[3]],
        [values[4], values[5], values[6], values[7]],
        [values[8], values[9], values[10], values[11]],
        [values[12],  values[13], values[14], values[15]]
      ])
    else:
      self.matrix = np.array([
        [values[0], values[1], 0, 0],
        [values[2], values[3], 0, 0],
        [0, 0, 1, 0],
        [values[4], values[5], 0, 1]
      ])
      
  def to_css(self):
    rows = [",".join(map(str,row)) for row in self.matrix]
    return f'matrix3d({",".join(rows)})'
    
  def rotate_by(self, angle_deg):
    matrix = np.array(self.identity)
    
    angle_rad = math.radians(angle_deg)
    matrix[0][0] = matrix[1][1] = math.cos(angle_rad)
    matrix[0][1] = matrix[1][0] = math.sin(angle_rad)
    matrix[1][0] *= -1
    
    self.matrix = np.dot(self.matrix, matrix)
    return self
    
  rotate_z_by = rotate_by
  
  def rotate_to(self, angle_deg):
    self.unmatrix()
    self.rotate_by(-self.rotation)
    self.rotate_by(angle_deg)
  
  @staticmethod
  def rotate_x_by(angle_deg):
    matrix = np.array(self.identity)
    
    angle_rad = math.radians(angle_deg)
    matrix[1][1] = matrix[2][2] = math.cos(angle_rad)
    matrix[1][2] = matrix[2][1] = math.sin(angle_rad)
    matrix[2][1] *= -1
    
    return matrix
    
  @staticmethod
  def rotate_y_by(angle_deg):
    matrix = np.array(Transforms.identity)
    
    angle_rad = math.radians(angle_deg)
    matrix[0][0] = matrix[2][2] = math.cos(angle_rad)
    matrix[0][2] = matrix[2][0] = math.sin(angle_rad)
    matrix[0][2] *= -1
    
    return matrix
    
  def scale_by(self, scale, scale_y=None):
    matrix = np.array(self.identity)
    
    matrix[0][0] = scale
    matrix[1][1] = scale if scale_y is None else scale_y

    self.matrix = np.dot(self.matrix, matrix)
    return self
    
  @staticmethod
  def scale_z_by(scale):
    matrix = np.array(Transforms.identity)
    
    matrix[2][2] = scale

    return matrix

  @staticmethod
  def skew_by(skew_angle_x_deg, skew_angle_y_deg=None):
    matrix = np.array(Transforms.identity)
    
    angle_x_rad = math.radians(skew_angle_x_deg)
    matrix[1][0] = math.tan(angle_x_rad)
    
    if skew_angle_y_deg is not None:
      angle_y_rad = math.radians(skew_angle_y_deg)
      matrix[0][1] = math.tan(angle_y_rad)
    
    return matrix
    
  @staticmethod
  def translate_by(x=0, y=0, z=0):
    matrix = np.array(Transforms.identity)
    
    matrix[3][0] = x
    matrix[3][1] = y
    matrix[3][2] = z

    return matrix


if __name__ == '__main__':
  
  css_transform = 'matrix(0.6156614753256583, 0.7880107536067218, -0.7880107536067219, 0.6156614753256583, -8.617463914053179, 70.183611446619)'
  css_transform = 'matrix(1, 0, 0, 1, 50, 50)'
  css_transform = 'matrix(0.9063077870366499, 0.42261826174069944, -0.42261826174069944, 0.9063077870366499, 50, 50)'
  #matrix = Transforms.css_to_matrix(css_transform)
  #print(matrix)

  t = Transform().rotate_matrix(25).rotate_matrix(30)
  t.unmatrix()
  print('New', t.rotation)

  rot25 = Transform.rotate_matrix(25)
  rot30 = Transform.rotate_matrix(30)
  rot_reverse = Transform.rotate_matrix(-55)
  
  
  total = np.dot(rot25, rot30)
  total = np.dot(total, rot_reverse)
  total = np.dot(total, rot_reverse)
  
  css = Transform.matrix_to_css(total)
  matrix = Transform.css_to_matrix(css)
  
  result = Transform.unmatrix(matrix)
  print('result', result)
