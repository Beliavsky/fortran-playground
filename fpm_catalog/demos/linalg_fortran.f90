program checked_lapack_operations
   use iso_fortran_env, only: dp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use linalg_fortran, only: linalg
   implicit none
   real(dp) :: a(3,3), inverse(3,3), vectors(3,3), eigenvalues(3), identity(3,3), determinant
   integer :: i
   a=reshape([2._dp,1._dp,0._dp,1._dp,2._dp,1._dp,0._dp,1._dp,2._dp],[3,3])
   identity=0
   do i=1,3
      identity(i,i)=1
   end do
   inverse=a
   if(.not.linalg%inv(inverse)) error stop 'Inverse failed'
   if(.not.all(ieee_is_finite(inverse))) error stop 'Nonfinite inverse'
   if(maxval(abs(matmul(a,inverse)-identity))>1.e-11_dp) error stop 'Inverse residual'
   determinant=linalg%det(a)
   if(abs(determinant-4._dp)>1.e-11_dp) error stop 'Determinant mismatch'
   vectors=a
   call linalg%eigh(vectors,eigenvalues)
   if(.not.all(ieee_is_finite(eigenvalues))) error stop 'Nonfinite eigenvalues'
   if(maxval(abs(eigenvalues-[2-sqrt(2._dp),2._dp,2+sqrt(2._dp)]))>1.e-11_dp) &
      error stop 'Eigenvalue mismatch'
   do i=1,3
      if(maxval(abs(matmul(a,vectors(:,i))-eigenvalues(i)*vectors(:,i)))>1.e-11_dp) &
         error stop 'Eigenpair residual'
   end do
   if(maxval(abs(matmul(transpose(vectors),vectors)-identity))>1.e-11_dp) &
      error stop 'Eigenvectors are not orthonormal'
   print '(a,f12.8)', 'Determinant: ',determinant
   print '(a,3f14.9)', 'Eigenvalues: ',eigenvalues
   print '(a,es12.4)', 'Inverse residual: ',maxval(abs(matmul(a,inverse)-identity))
   print *, 'PASS linalg_fortran'
end program checked_lapack_operations
