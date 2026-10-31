! Independent API consumer; MIT: licenses/conversion-triangulation-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use str2real_m,only:str2real
   implicit none
   character(len=12),parameter::mantissas(*)=[character(len=12):: &
      '0','1','25','12345','9876543','.125','12.5','0.000125']
   real(wp),parameter::coefficients(*)=[0.0_wp,1.0_wp,25.0_wp,12345.0_wp,9876543.0_wp, &
      0.125_wp,12.5_wp,0.000125_wp]
   integer,parameter::exponents(*)=[-100,-12,-1,0,1,12,100]
   character(len=32),parameter::boundary(*)=[character(len=32):: &
      '1234567890123456e0','-123456789012345E0', &
      '0.123456789012345678901234e0','-.123456789012345678901234e0']
   real(wp),parameter::boundary_values(*)=[1234567890123456.0_wp,-123456789012345.0_wp, &
      0.123456789012345678901234_wp,-0.123456789012345678901234_wp]
   character(len=:),allocatable::text,prefix
   character(len=8)::suffix
   real(wp)::reference,parsed,read_value,error,worst_arithmetic,worst_read
   integer::i,sign,notation,j,status,calls
   calls=0; worst_arithmetic=0; worst_read=0
   do i=1,size(mantissas)
      do sign=-1,1,2
         prefix=''
         if (sign<0) prefix='-'
         text=prefix//trim(mantissas(i))
         reference=sign*coefficients(i)
         call check()
         do notation=1,2
            do j=1,size(exponents)
               write(suffix,'(sp,i0)') exponents(j)
               text=prefix//trim(mantissas(i))
               if (notation==1) then
                  text=text//'E'//trim(suffix)
               else
                  text=text//'e'//trim(suffix)
               end if
               reference=sign*coefficients(i)*10.0_wp**exponents(j)
               call check()
            end do
         end do
      end do
   end do
   do i=1,size(boundary)
      text=trim(boundary(i)); reference=boundary_values(i)
      call check()
   end do
   if (calls/=244) error stop 'accounting'
   print '(a,i0)', 'Valid decimal conversions: ',calls
   print '(a)', 'Two independent references per conversion: arithmetic and formatted READ.'
   print '(a)', 'Both signs; plain decimals; E/e with signed exponents -100..100; long mantissas.'
   print '(a,es12.4)', 'Maximum relative arithmetic-reference error: ',worst_arithmetic
   print '(a,es12.4)', 'Maximum relative formatted-READ error: ',worst_read
   print '(a)', 'PASS str2real-decimal-reference'
contains
   subroutine check()
      if (len(text)>28) error stop 'fixture string length'
      parsed=str2real(text)
      read(text,*,iostat=status) read_value
      if (status/=0.or..not.ieee_is_finite(read_value)) error stop 'reference READ failed'
      if (.not.ieee_is_finite(parsed)) error stop 'nonfinite conversion'
      if (reference==0) then
         if (parsed/=0.or.read_value/=0) error stop 'zero conversion'
      else
         error=abs(parsed-reference)/abs(reference)
         if (error>5e-14_wp) then
            print *,text,parsed,reference,error
            error stop 'arithmetic decimal reference'
         end if
         worst_arithmetic=max(worst_arithmetic,error)
         error=abs(parsed-read_value)/abs(read_value)
         if (error>5e-14_wp) error stop 'formatted READ reference'
         worst_read=max(worst_read,error)
      end if
      calls=calls+1
   end subroutine
end program
