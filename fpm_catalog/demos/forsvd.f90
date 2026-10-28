! Compare rank-one and rank-two approximations of a small matrix.
program demo_forsvd
   use kinds, only: rk
   use forsvd, only: svd
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(rk) :: a(4,3), work(4,3), u(4,4), s(3), vt(3,3), approx(4,3), errors(3)
   integer :: i,j,k
   a = reshape([3._rk,0._rk,0._rk,0._rk,0._rk,2._rk,0._rk,0._rk,0._rk,0._rk,1._rk,0._rk],[4,3])
   ! LAPACK overwrites its input workspace; preserve A for independent checks.
   work = a
   call svd(work,u,s,vt,method='gesvd')
   if (.not. all(ieee_is_finite(s))) error stop 'Nonfinite singular values'
   if (.not. all(ieee_is_finite(u)) .or. .not. all(ieee_is_finite(vt))) error stop 'Nonfinite vectors'
   if (maxval(abs(s-[3._rk,2._rk,1._rk]))>1e-11_rk) error stop 'Incorrect singular values'
   approx = 0
   print '(a)', 'Rank    Frobenius reconstruction error'
   do k=1,3
      do j=1,3
         do i=1,4
            approx(i,j) = approx(i,j)+s(k)*u(i,k)*vt(k,j)
         end do
      end do
      errors(k) = norm2(a-approx)
      print '(i3,es22.10)', k, errors(k)
   end do
   if (maxval(abs(errors-[sqrt(5._rk),1._rk,0._rk]))>1e-11_rk) error stop 'Incorrect approximation'
   print '(a)', 'PASS forsvd'
end program
