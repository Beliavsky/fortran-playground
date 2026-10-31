! Original D4a1 API driver. MIT: licenses/boundary-spectral-drivers-MIT.txt.
program main
   use iso_fortran_env, only: dp=>real64
   use linalg_fortran, only: linalg
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer,parameter :: n=20
   real(dp) :: a(n,n),vectors(n,n),eigenvalues(n),identity(n,n),gram(n,n),weighted(n,n)
   real(dp) :: expected,product(n),exact_vector(n),residual,maximum_error,reconstruction
   integer :: i,j
   a=0; identity=0
   do i=1,n
      a(i,i)=2
      identity(i,i)=1
      if(i<n) then
         a(i,i+1)=-1
         a(i+1,i)=-1
      end if
   end do
   vectors=a
   call linalg%eigh(vectors,eigenvalues)
   if(.not.all(ieee_is_finite(eigenvalues)) .or. .not.all(ieee_is_finite(vectors))) &
      error stop 'nonfinite dense eigensystem'
   maximum_error=0
   print '(a)', 'Index       Computed eigenvalue        Exact eigenvalue          Residual'
   do j=1,n
      expected=4*sin(real(j,dp)*acos(-1._dp)/(2*(n+1)))**2
      maximum_error=max(maximum_error,abs(eigenvalues(j)-expected))
      product=2*vectors(:,j)
      product(2:n)=product(2:n)-vectors(:n-1,j)
      product(:n-1)=product(:n-1)-vectors(2:n,j)
      residual=sqrt(sum((product-eigenvalues(j)*vectors(:,j))**2))
      if(abs(eigenvalues(j)-expected)>1.e-11_dp .or. residual>1.e-11_dp) error stop 'known dense eigenpair'
      exact_vector=[(sqrt(2._dp/(n+1))*sin(real(i*j,dp)*acos(-1._dp)/(n+1)),i=1,n)]
      if(abs(abs(dot_product(vectors(:,j),exact_vector))-1)>1.e-8_dp) error stop 'known sine eigenvector'
      weighted(:,j)=vectors(:,j)*eigenvalues(j)
      if(j<=3 .or. j>=n-2) print '(i3,2f24.15,es14.4)',j,eigenvalues(j),expected,residual
   end do
   gram=matmul(transpose(vectors),vectors)
   if(maxval(abs(gram-identity))>1.e-11_dp) error stop 'dense eigenvector orthonormality'
   reconstruction=maxval(abs(matmul(weighted,transpose(vectors))-a))
   if(reconstruction>1.e-11_dp) error stop 'dense spectral reconstruction'
   print '(a,2es14.5)', 'All 20 checked; maximum eigenvalue/reconstruction errors: ',maximum_error,reconstruction
   print '(a)', 'Six listed eigenpairs use the same n=20 Dirichlet matrix as the ARPACK driver.'
   print '(a)', 'PASS linalg-poisson-eigenpairs'
end program
