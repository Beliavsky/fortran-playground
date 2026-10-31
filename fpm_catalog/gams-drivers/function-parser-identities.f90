! Independent API consumer; MIT: licenses/expression-evaluation-drivers-MIT.txt.
program main
   use function_parser,only:fparser
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
   type(fparser)::expression
   character(len=32),parameter::bad_parse(*)=[character(len=32)::'pgx+','(pgx','unknown(pgx)']
   character(len=32),parameter::bad_eval(*)=[character(len=32)::'sqrt(pgx)','log(pgx)','1/(pgx-pgx)']
   real(wp)::inputs(2),saved(2)
   checks=0; rejected=0; recovered=0; worst=0
   do ie=1,size(expressions)
      call expression%clear_errors()
      call expression%destroy()
      call expression%parse(trim(expressions(ie)),['pgx','pgy'])
      if (expression%error()) error stop 'valid expression rejected'
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
            inputs=[x,y]; saved=inputs
            call expression%evaluate(inputs,result)
            if (expression%error()) error stop 'valid evaluation rejected'
            if (any(inputs/=saved)) error stop 'changed variable inputs'
            call check(result,reference)
         end do
      end do
   end do
   do ie=1,size(bad_parse)
      call expression%clear_errors()
      call expression%destroy()
      call expression%parse(trim(bad_parse(ie)),['pgx','pgy'])
      if (.not.expression%error()) error stop 'missing parse error'
      rejected=rejected+1
      call recovery()
   end do
   do ie=1,size(bad_eval)
      call expression%clear_errors()
      call expression%destroy()
      call expression%parse(trim(bad_eval(ie)),['pgx','pgy'])
      if (expression%error()) error stop 'domain probe parse failed'
      call expression%evaluate([-1.0_wp,0.5_wp],result)
      if (.not.expression%error()) error stop 'missing evaluation error'
      rejected=rejected+1
      call recovery()
   end do
   call expression%clear_errors()
   call expression%destroy()
   if (checks/=286.or.rejected/=6.or.recovered/=6) error stop 'accounting'
   print '(a,i0)', 'Independent expression value references: ',checks
   print '(a,i0,a,i0)', 'Expected rejected requests: ',rejected,'; successful recoveries: ',recovered
   print '(a,es12.4)', 'Maximum normalized expression error: ',worst
   print '(a)', 'PASS function-parser-identities'
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
   subroutine recovery()
      call expression%clear_errors()
      call expression%destroy()
      call expression%parse('pgx+pgy',['pgx','pgy'])
      if (expression%error()) error stop 'recovery parse'
      call expression%evaluate([0.25_wp,-0.5_wp],result)
      if (expression%error()) error stop 'recovery evaluation'
      call check(result,-0.25_wp)
      recovered=recovered+1
   end subroutine
end program
