! Independent API consumer; MIT: licenses/expression-evaluation-drivers-MIT.txt.
program main
   use M_calculator,only:dnum0
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   character(len=96),parameter::expressions(*)=[character(len=96):: &
      'pgx+2*pgy','(pgx+2)*(pgy-3)','pgx**2+3*pgx*pgy+pgy**2', &
      'sin(pgx)**2+cos(pgx)**2','exp(log(pgx+4))','sqrt((pgx+4)**2)', &
      'abs(pgx-pgy)','sin(pgx+pgy)-sin(pgx)*cos(pgy)-cos(pgx)*sin(pgy)', &
      '(pgx-pgy)/(pgx+4)','pgx**3-3*pgx**2*pgy+3*pgx*pgy**2-pgy**3', &
      'log(exp(pgy/4))','2+3*4','(2+3)*4','-(pgx+pgy)']
   real(wp),parameter::xs(*)=[-2.0_wp,-0.5_wp,0.0_wp,0.75_wp,2.0_wp]
   real(wp),parameter::ys(*)=[-1.5_wp,0.0_wp,0.5_wp,1.25_wp]
   real(wp)::x,y,result,reference,error,worst
   integer::ie,ix,iy,checks,rejected,recovered
   integer::status,assignment_calls
   character(len=32),parameter::bad_parse(*)=[character(len=32)::'(1+2','1+@','1+*2']
   character(len=40)::number
   real(wp)::assigned
   checks=0; rejected=0; recovered=0; worst=0
   assignment_calls=0
   do ie=1,size(expressions)
      do ix=1,size(xs)
         x=xs(ix)
         do iy=1,size(ys)
            y=ys(iy)
            select case(ie)
            case(1)
               reference=x+2*y
            case(2)
               reference=(x+2)*(y-3)
            case(3)
               reference=x*x+3*x*y+y*y
            case(4)
               reference=1
            case(5,6)
               reference=x+4
            case(7)
               reference=abs(x-y)
            case(8)
               reference=0
            case(9)
               reference=(x-y)/(x+4)
            case(10)
               reference=(x-y)**3
            case(11)
               reference=y/4
            case(12)
               reference=14
            case(13)
               reference=20
            case(14)
               reference=-x-y
            end select
            write(number,'(es26.17e3)') x
            assigned=dnum0('pgx='//trim(adjustl(number)),status)
            if (status/=0.or..not.ieee_is_finite(assigned)) error stop 'x assignment status'
            if (abs(assigned-x)>1e-14_wp) error stop 'x assignment value'
            write(number,'(es26.17e3)') y
            assigned=dnum0('pgy='//trim(adjustl(number)),status)
            if (status/=0.or..not.ieee_is_finite(assigned)) error stop 'y assignment status'
            if (abs(assigned-y)>1e-14_wp) error stop 'y assignment value'
            assignment_calls=assignment_calls+2
            result=dnum0(trim(expressions(ie)),status)
            if (status/=0) error stop 'valid expression status'
            call check(result,reference)
         end do
      end do
   end do
   do ie=1,size(bad_parse)
      result=dnum0(trim(bad_parse(ie)),status)
      if (status==0) error stop 'missing syntax error'
      rejected=rejected+1
      result=dnum0('pgx+pgy',status)
      if (status/=0) error stop 'recovery status'
      call check(result,xs(size(xs))+ys(size(ys)))
      recovered=recovered+1
   end do
   if (checks/=283.or.assignment_calls/=560.or.rejected/=3.or.recovered/=3) error stop 'accounting'
   print '(a,i0)', 'Checked variable assignments: ',assignment_calls
   print '(a,i0)', 'Independent expression value references: ',checks
   print '(a,i0,a,i0)', 'Expected rejected requests: ',rejected,'; successful recoveries: ',recovered
   print '(a,es12.4)', 'Maximum normalized expression error: ',worst
   print '(a)', 'PASS m-calculator-identities'
contains
   subroutine check(value,expected)
      real(wp),intent(in)::value,expected
      if (.not.ieee_is_finite(value)) error stop 'nonfinite expression value'
      error=abs(value-expected)/max(1.0_wp,abs(expected))
      if (error>2e-12_wp) then
         print *, 'Expression, result, expected, error:',ie,value,expected,error
         error stop 'independent expression reference'
      end if
      worst=max(worst,error); checks=checks+1
   end subroutine
end program
