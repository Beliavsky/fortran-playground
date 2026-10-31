! Independent API consumer; MIT: licenses/jacobian-transforms-drivers-MIT.txt.
program main
   use iso_c_binding,only:c_float,c_double
   use ieee_arithmetic,only:ieee_is_finite
   use vector_3d,only:vec3d
   use matrix_4f,only:mat4f
   implicit none
   real(c_float),parameter::pi=acos(-1.0_c_float)
   real(c_float),parameter::angles(*)=[-2*pi,-pi,-pi/2,-pi/3,0.0_c_float,pi/6,pi/2,pi,2*pi]
   real(c_float),parameter::translations(3,4)=reshape([0.0_c_float,0.0_c_float,0.0_c_float, &
      1.0_c_float,-2.0_c_float,0.5_c_float,-4.0_c_float,0.0_c_float,2.0_c_float, &
      0.25_c_float,0.5_c_float,-0.75_c_float],[3,4])
   real(c_float),parameter::points(4,3)=reshape([1.0_c_float,2.0_c_float,3.0_c_float,1.0_c_float, &
      -2.0_c_float,0.5_c_float,0.0_c_float,1.0_c_float,1.0_c_float,-1.0_c_float,2.0_c_float,0.0_c_float],[4,3])
   type(vec3d)::a,b,result
   type(mat4f)::transform
   real(c_double)::av(3),bv(3),values(3),expected(4),p(4),t(3),co,si,error,worst_v,worst_t,value,det
   real(c_float)::matrix(4,4),actual(4)
   integer::i,j,k,ia,it,mode,ip,vector_calls,transforms,point_checks
   vector_calls=0; transforms=0; point_checks=0; worst_v=0; worst_t=0
   do i=1,24
      av=[real(i,c_double)/8,real(i-12,c_double)/4,(-1.0_c_double)**i/2]
      bv=[real(25-i,c_double)/4,-real(i,c_double)/8,real(mod(i,5)-2,c_double)]
      a=vec3d(av); b=vec3d(bv)
      result=a+b; values=result%as_array()
      if (.not.all(ieee_is_finite(values))) error stop 'nonfinite vector sum'
      error=maxval(abs(values-(av+bv)))
      if (error>1e-13_c_double) error stop 'component sum'
      worst_v=max(worst_v,error)
      result=a*b; values=result%as_array()
      if (.not.all(ieee_is_finite(values))) error stop 'nonfinite vector product'
      error=maxval(abs(values-av*bv))
      if (error>1e-13_c_double) error stop 'component product'
      worst_v=max(worst_v,error)
      if (any(a%as_array()/=av).or.any(b%as_array()/=bv)) error stop 'changed vectors'
      vector_calls=vector_calls+2
   end do
   do ia=1,size(angles)
      co=cos(real(angles(ia),c_double)); si=sin(real(angles(ia),c_double))
      do it=1,size(translations,2)
         t=real(translations(:,it),c_double)
         do mode=1,2
            call transform%identity()
            if (mode==1) then
               call transform%translate(translations(1,it),translations(2,it),translations(3,it))
               call transform%rotate_z(angles(ia))
            else
               call transform%rotate_z(angles(ia))
               call transform%translate(translations(1,it),translations(2,it),translations(3,it))
            end if
            matrix=reshape(transform%data,[4,4])
            if (.not.all(ieee_is_finite(matrix))) error stop 'nonfinite transform'
            do j=1,3
               do i=1,3
                  value=0
                  do k=1,3
                     value=value+real(matrix(k,i),c_double)*real(matrix(k,j),c_double)
                  end do
                  if (i==j) value=value-1
                  if (abs(value)>2e-6_c_double) error stop 'rotation orthogonality'
               end do
            end do
            det=real(matrix(1,1),c_double)*(real(matrix(2,2),c_double)*matrix(3,3)- &
               real(matrix(2,3),c_double)*matrix(3,2))-real(matrix(1,2),c_double)* &
               (real(matrix(2,1),c_double)*matrix(3,3)-real(matrix(2,3),c_double)*matrix(3,1))+ &
               real(matrix(1,3),c_double)*(real(matrix(2,1),c_double)*matrix(3,2)- &
               real(matrix(2,2),c_double)*matrix(3,1))
            if (abs(det-1)>2e-6_c_double) error stop 'rotation determinant'
            do ip=1,size(points,2)
               p=real(points(:,ip),c_double)
               if (mode==2) p(:3)=p(:3)+t*p(4)
               expected=[co*p(1)-si*p(2),si*p(1)+co*p(2),p(3),p(4)]
               if (mode==1) expected(:3)=expected(:3)+t*p(4)
               actual=matmul(matrix,points(:,ip))
               if (.not.all(ieee_is_finite(actual))) error stop 'nonfinite transformed point'
               error=maxval(abs(real(actual,c_double)-expected))/max(1.0_c_double,maxval(abs(expected)))
               if (error>2e-6_c_double) error stop 'independent transform reference'
               worst_t=max(worst_t,error); point_checks=point_checks+4
            end do
            transforms=transforms+1
         end do
      end do
   end do
   if (vector_calls/=48.or.transforms/=72.or.point_checks/=864) error stop 'accounting'
   print '(a,i0)', 'Double-precision vector operations: ',vector_calls
   print '(a,i0,a,i0)', 'Single-precision rigid transforms: ',transforms,'; coordinate references: ',point_checks
   print '(a)', 'Both composition orders; points and directions; orthogonality and determinant.'
   print '(a,es12.4)', 'Maximum vector component error: ',worst_v
   print '(a,es12.4)', 'Maximum normalized transform error: ',worst_t
   print '(a)', 'PASS fglm-transform-reference'
end program
