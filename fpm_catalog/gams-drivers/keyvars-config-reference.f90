! Independent MIT API consumer; see licenses/state-ten-drivers-MIT.txt.
program keyvars_reference
   use, intrinsic :: iso_fortran_env, only: real64
   use keyvars, only: keyvar,get_values
   implicit none
   character(6), parameter :: true_words(*)=['true  ','.true.','T     ','yes   ','Yes   ','YES   ']
   integer, target :: steps,untouched
   real(real64), target :: dt
   logical, target :: enabled
   character(40), target :: label
   integer :: fixture,unit,cases
   cases=0
   do fixture=1,36
      steps=-999; dt=-999; enabled=.false.; label='unset'; untouched=123
      open(newunit=unit,file='keyvars-reference.ini',status='replace',action='write')
      write(unit,'(a)') '# Generated reference settings','[run]'
      write(unit,'(a,i0,a)') 'steps = ',3*fixture-20,' # integer comment'
      write(unit,'(a,f12.6)') 'dt = ',real(fixture-18,real64)/8
      write(unit,'(a)') 'enabled = '//trim(true_words(1+modulo(fixture-1,6)))
      write(unit,'(a,i0)') 'label = run ',fixture
      close(unit)
      call get_values('keyvars-reference.ini',[keyvar('steps',steps,'steps'),keyvar('dt',dt,'dt'), &
         keyvar('enabled',enabled,'flag'),keyvar('label',label,'name'),keyvar('missing',untouched,'default')])
      if (steps/=3*fixture-20 .or. dt/=real(fixture-18,real64)/8) error stop 'keyvars numeric reference'
      if (.not.enabled .or. untouched/=123) error stop 'keyvars flag/default reference'
      block
         character(40) :: expected
         write(expected,'(a,i0)') 'run ',fixture
         if (label/=expected) error stop 'keyvars string reference'
      end block
      cases=cases+1
   end do
   open(newunit=unit,file='keyvars-reference.ini',status='old'); close(unit,status='delete')
   print '(a)', '36 generated INI files; 180 exact scalar/default references.'
   print '(a)', 'Signed integer/dyadic real values, six true spellings, comments, string values and absent-key defaults.'
   print '(a)', 'Wildcard sections only; malformed input, false spellings, section-specific matching and CLI overrides unverified.'
   print '(a)', 'PASS keyvars-config-reference'
end program
