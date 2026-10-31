! Original G2a API driver. MIT: licenses/optimization-api-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use conmax_module, only: slnpro
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp) :: tableau(7,4),x(3),y(6),matrix(2,2),rhs(2),scales(2),lambda(2),expected(2)
   real(wp),parameter :: first(*)=[2._wp,5._wp,-3._wp],second(*)=[4._wp,1._wp,7._wp]
   real(wp) :: objective,certificate,gap
   integer :: iyrct(6),ixrct(6),iycct(3),status,c
   do c=1,3
      select case(c)
      case(1)
         scales=[1._wp,1._wp]
      case(2)
         scales=[.5_wp,3._wp]
      case(3)
         scales=[4._wp,.25_wp]
      end select
      matrix(1,:)=[-1._wp,-1._wp]*scales(1)
      matrix(2,:)=[1._wp,-1._wp]*scales(2)
      rhs=[-first(c)*scales(1),second(c)*scales(2)]
      expected=[(first(c)+second(c))/2,(first(c)-second(c))/2]
      lambda=.5_wp/scales
      ! Nonnegative dual weights combine the inequalities into an upper bound on -y.
      if(maxval(abs(matmul(transpose(matrix),lambda)-[0._wp,-1._wp]))>1.e-12_wp) &
         error stop 'independent dual certificate'
      certificate=dot_product(lambda,rhs)
      tableau=0; x=0; y=0
      iyrct=0; ixrct=0; iycct=0
      tableau(1:2,1:2)=matrix
      tableau(1:2,3)=rhs
      tableau(3,1:2)=[0._wp,1._wp] ! SLNPRO maximizes the negative of this row times x.
      iyrct(1)=-1
      call slnpro(tableau,2,2,iyrct,y,ixrct,iycct,2,2,x,status)
      if(status/=0) error stop 'LP status'
      if(.not.all(ieee_is_finite(x(:2)))) error stop 'nonfinite LP solution'
      if(maxval(abs(x(:2)-expected))>1.e-9_wp) error stop 'known LP solution'
      if(maxval(matmul(matrix,x(:2))-rhs)>1.e-9_wp) error stop 'LP feasibility'
      objective=-x(2)
      gap=certificate-objective
      if(abs(gap)>1.e-9_wp) error stop 'LP primal-dual gap'
      if(.not.ieee_is_finite(tableau(3,3))) error stop 'nonfinite reported LP objective'
      if(abs(tableau(3,3)-objective)>1.e-9_wp) error stop 'reported LP objective'
      print '(a,i0,a,2f12.6,a,f12.6,a,es12.3)', 'Case ',c,': x,y=',x(:2), &
         '; maximum -y=',objective,'; certificate gap=',gap
   end do
   print '(a)', 'Free variables, mixed-sign optima and rescaled inequalities checked.'
   print '(a)', 'PASS conmax-linear-program-certificate'
end program
