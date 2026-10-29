program checked_configuration
   use iso_fortran_env, only: dp=>real64
   use keyvars, only: keyvar,get_values
   implicit none
   integer,target::steps
   real(dp),target::dt
   logical,target::enabled
   character(24),target::label
   integer::unit,status
   character(*),parameter::filename='playground-settings.ini'
   ! A tiny file created inside the sandbox; no user-supplied data is needed.
   open(newunit=unit,file=filename,status='replace',action='write',iostat=status)
   if(status/=0) error stop 'Cannot create configuration'
   write(unit,'(a)') '# Scientific run settings', '[run]', &
      'steps = 12 # integer parameter','dt = 0.25','enabled = yes','label = heat equation'
   close(unit)
   steps=-1;dt=-1;enabled=.false.;label='unset'
   call get_values(filename,[keyvar('steps',steps,'Number of time steps'), &
      keyvar('dt',dt,'Time step'),keyvar('enabled',enabled,'Enable this run'), &
      keyvar('label',label,'Description')])
   if(steps/=12 .or. abs(dt-0.25_dp)>1.e-12_dp) error stop 'Numeric parameters mismatch'
   if(.not.enabled .or. trim(label)/='heat equation') error stop 'Other parameters mismatch'
   print '(a,i0,a,f6.3)', 'Configuration: steps=',steps,'  dt=',dt
   print '(a,l1,a)', 'enabled=',enabled,'  label='//trim(label)
   open(newunit=unit,file=filename,status='old')
   close(unit,status='delete')
   print *, 'PASS io_utilities'
end program checked_configuration
