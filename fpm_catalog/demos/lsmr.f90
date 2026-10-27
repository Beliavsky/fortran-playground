module example_matrix
   use lsmrDataModule, only: ip => lsmr_ip, wp => lsmr_wp
   implicit none
contains
   subroutine multiply(m,n,x,y)
      integer(ip), intent(in) :: m,n
      real(wp), intent(in) :: x(n)
      real(wp), intent(inout) :: y(m)
      y = y+[2.0_wp*x(1),3.0_wp*x(2)]
   end subroutine
   subroutine transpose_multiply(m,n,x,y)
      integer(ip), intent(in) :: m,n
      real(wp), intent(inout) :: x(n)
      real(wp), intent(in) :: y(m)
      x = x+[2.0_wp*y(1),3.0_wp*y(2)]
   end subroutine
end module example_matrix

program main
   use example_matrix
   use lsmrModule, only: lsmr
   implicit none
   real(wp) :: x(2), norm_a, condition, residual, normal_residual, norm_x
   integer(ip) :: status, iterations
   ! Matrix products avoid storing a dense matrix; A=diag(2,3), b=(4,9).
   call lsmr(2_ip,2_ip,multiply,transpose_multiply,[4.0_wp,9.0_wp],0.0_wp, &
      1.e-12_wp,1.e-12_wp,1.e8_wp,20_ip,0_ip,0_ip,x,status,iterations, &
      norm_a,condition,residual,normal_residual,norm_x)
   if (status < 1 .or. status > 2) error stop 'LSMR did not converge'
   if (maxval(abs(x-[2.0_wp,3.0_wp])) > 1.e-10_wp) error stop 'incorrect sparse solution'
   print *, 'LSMR solution:', x
   print *, 'Residual norm:', residual
   print *, 'PASS lsmr'
end program main
