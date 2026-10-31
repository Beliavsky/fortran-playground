! Original D9c API driver. MIT: licenses/linear-algebra-api-drivers-MIT.txt.
program main
   use kinds, only: rk
   use forinv, only: inv
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(rk) :: a(3,2),reference(2,3),square(3,3),square_reference(3,3),u(3),v(2),x(2)
   real(rk),allocatable :: result(:,:)
   integer :: i,j,cases
   cases=0
   u=[1._rk,2._rk,3._rk]
   v=[1._rk,2._rk]
   do i=1,3
      do j=1,2
         a(i,j)=u(i)*v(j)
         ! (u*v^T)^+ = v*u^T / ((u^T*u)*(v^T*v)) = v*u^T/70.
         reference(j,i)=v(j)*u(i)/70
      end do
   end do
   call check(a,reference,result)
   x=matmul(result,u)
   if(maxval(abs(x-[.2_rk,.4_rk]))>1.e-11_rk) error stop 'minimum-norm solution'
   print '(a,2f16.10)', 'Rank-one minimum-norm solution: ',x
   ! Two orthogonal columns, squared norms 9 and 5, give an explicit full-rank inverse.
   a(:,1)=[1._rk,2._rk,2._rk]
   a(:,2)=[2._rk,-1._rk,0._rk]
   reference(1,:)=a(:,1)/9
   reference(2,:)=a(:,2)/5
   call check(a,reference,result)
   call check(transpose(a),transpose(reference),result)
   square=0
   square_reference=0
   square(1,1)=2; square(3,3)=4
   square_reference(1,1)=.5_rk; square_reference(3,3)=.25_rk
   call check(square,square_reference,result)
   a=0; reference=0
   call check(a,reference,result)
   if(cases/=5) error stop 'case count'
   print '(a,i0)', 'Known pseudoinverses and all four Moore-Penrose identities checked: ',cases
   print '(a)', 'Tall, wide, rank-one, singular diagonal and zero matrices; explicit cutoff 1e-10.'
   print '(a)', 'PASS forinv-pseudoinverse-reference'
contains
   subroutine check(original,expected,pseudoinverse)
      real(rk),intent(in) :: original(:,:),expected(:,:)
      real(rk),allocatable,intent(out) :: pseudoinverse(:,:)
      real(rk),allocatable :: workspace(:,:),left(:,:),right(:,:)
      real(rk) :: errors(5)
      ! The pinned ForSVD dependency may overwrite its input; preserve the reference matrix.
      workspace=original
      pseudoinverse=inv(workspace,method='gesvd',tol=1.e-10_rk)
      if(.not.all(ieee_is_finite(pseudoinverse))) error stop 'nonfinite pseudoinverse'
      left=matmul(original,pseudoinverse)
      right=matmul(pseudoinverse,original)
      errors(1)=maxval(abs(pseudoinverse-expected))/max(1._rk,maxval(abs(expected)))
      errors(2)=maxval(abs(matmul(left,original)-original))/max(1._rk,maxval(abs(original)))
      errors(3)=maxval(abs(matmul(right,pseudoinverse)-pseudoinverse))/max(1._rk,maxval(abs(pseudoinverse)))
      errors(4)=maxval(abs(left-transpose(left)))/max(1._rk,maxval(abs(left)))
      errors(5)=maxval(abs(right-transpose(right)))/max(1._rk,maxval(abs(right)))
      if(.not.all(ieee_is_finite(errors)) .or. any(errors>1.e-11_rk)) error stop 'pseudoinverse references'
      cases=cases+1
      print '(a,i0,a,5es12.3)', 'Case ',cases,' reference and identity errors: ',errors
   end subroutine
end program
