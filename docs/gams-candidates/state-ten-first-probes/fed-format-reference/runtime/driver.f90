! Independent MIT API consumer; see licenses/state-ten-drivers-MIT.txt.
program format_reference
   use fed, only: format,fed_int=>int,fed_real=>real,fed_char=>char,operator(//)
   implicit none
   integer, parameter :: integers(*)=[-1000,-1,0,7,123456]
   real, parameter :: reals(*)=[-12.5,-0.125,0.0,0.25,999.5]
   character(128) :: actual,expected,spec
   integer :: width,minimum,decimals,i,cases
   cases=0
   do width=1,12
      do minimum=0,min(width,6)
         write(spec,'("(I",i0,".",i0,")")') width,minimum
         do i=1,size(integers)
            write(actual,format(fed_int(width,minimum))) integers(i)
            write(expected,spec) integers(i)
            if (actual/=expected) then
               print *, 'integer width/minimum/value: ',width,minimum,integers(i)
               print *, 'FED: [',trim(actual),'] native: [',trim(expected),']'
               error stop 'FED integer descriptor reference'
            end if
            cases=cases+1
         end do
      end do
   end do
   do width=4,18,2
      do decimals=0,4
         write(spec,'("(F",i0,".",i0,")")') width,decimals
         do i=1,size(reals)
            write(actual,format(fed_real(width,decimals))) reals(i)
            write(expected,spec) reals(i)
            if (actual/=expected) error stop 'FED real descriptor reference'
            cases=cases+1
         end do
      end do
   end do
   do i=1,size(integers)
      write(actual,format(fed_int(6)//fed_char()//fed_real(12,4))) integers(i),' | ',reals(i)
      write(expected,'(I6,A,F12.4)') integers(i),' | ',reals(i)
      if (actual/=expected) error stop 'FED concatenated descriptor reference'
      cases=cases+1
   end do
   print '(a,i0)', 'Exact comparisons against independently constructed native Fortran formats: ',cases
   print '(a)', 'Integer widths/minimum digits, fixed-point decimals, overflow fields and concatenated columns.'
   print '(a)', 'Exponential/complex/user-defined descriptors, locale and cross-compiler rounding unverified.'
   print '(a)', 'PASS fed-format-reference'
end program
