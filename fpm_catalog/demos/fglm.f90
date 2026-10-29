program demo_geometric_math
   use, intrinsic :: iso_c_binding, only: c_float, c_double
   use vector_3d, only: vec3d
   use matrix_4f, only: mat4f
   implicit none
   type(vec3d) :: a, b, c
   type(mat4f) :: transform
   real(c_float) :: point(4), result(4), matrix(4, 4)

   a = vec3d([1.0_c_double, 2.0_c_double, 3.0_c_double])
   b = vec3d([4.0_c_double, -1.0_c_double, 2.0_c_double])
   c = a + b
   if (any(abs(c%as_array() - [5.0_c_double, 1.0_c_double, 5.0_c_double]) > 1.e-12_c_double)) &
      error stop 'vector addition'
   c = a*b
   if (any(abs(c%as_array() - [4.0_c_double, -2.0_c_double, 6.0_c_double]) > 1.e-12_c_double)) &
      error stop 'component multiplication'
   print '(a, f8.3)', 'Dot product from component multiplication: ', sum(c%as_array())

   point = [1.0_c_float, 2.0_c_float, 3.0_c_float, 1.0_c_float]
   call transform%translate(10.0_c_float, -2.0_c_float, 1.0_c_float)
   matrix = reshape(transform%data, [4, 4])
   result = matmul(matrix, point)
   if (maxval(abs(result - [11.0_c_float, 0.0_c_float, 4.0_c_float, 1.0_c_float])) > 5.e-6_c_float) &
      error stop 'translation'
   print '(a, 3f9.3)', 'Translated point: ', result(:3)

   call transform%identity()
   call transform%rotate_z(acos(-1.0_c_float)/2)
   result = matmul(reshape(transform%data, [4, 4]), [1.0_c_float, 0.0_c_float, 0.0_c_float, 1.0_c_float])
   if (maxval(abs(result - [0.0_c_float, 1.0_c_float, 0.0_c_float, 1.0_c_float])) > 5.e-6_c_float) &
      error stop 'quarter-turn rotation'
   print '(a, 3f9.3)', 'Unit x vector rotated 90 degrees about z: ', result(:3)
   print '(a)', 'PASS fglm'
end program demo_geometric_math
