! Independent MIT API consumer; see licenses/state-ten-drivers-MIT.txt.
program config_reference
   use, intrinsic :: iso_fortran_env, only: real64
   use m_config, only: CFG_t,CFG_add,CFG_get,CFG_get_size,CFG_read_file,CFG_clear
   implicit none
   integer :: fixture,unit,n,i,checks
   checks=0
   do fixture=1,24
      block
         type(CFG_t) :: config
         integer :: steps,retained
         logical :: enabled
         real(real64) :: dt
         real(real64), allocatable :: samples(:)
         character(40) :: title,expected
         call CFG_add(config,'steps',-999,'integer')
         call CFG_add(config,'solver%dt',-999.0_real64,'time')
         call CFG_add(config,'enabled',.false.,'flag')
         call CFG_add(config,'title','default','text')
         call CFG_add(config,'retained',42,'unchanged default')
         call CFG_add(config,'samples',[0.0_real64],'dynamic array',dynamic_size=.true.)
         n=1+modulo(fixture,8)
         open(newunit=unit,file='config-reference.cfg',status='replace',action='write')
         write(unit,'(a,i0)') 'steps = ',5*fixture-37
         write(unit,'(a,f12.6)') 'solver%dt = ',real(fixture-12,real64)/8
         write(unit,'(a)') 'enabled = .true.'
         write(expected,'(a,i0)') 'run_',fixture
         write(unit,'(a)') 'title = '//trim(expected)
         write(unit,'(a,*(f12.6,1x))') 'samples = ',[(real(i-fixture,real64)/8,i=1,n)]
         close(unit)
         call CFG_read_file(config,'config-reference.cfg')
         call CFG_get(config,'steps',steps); call CFG_get(config,'solver%dt',dt)
         call CFG_get(config,'enabled',enabled); call CFG_get(config,'title',title)
         call CFG_get(config,'retained',retained); call CFG_get_size(config,'samples',i)
         if (i/=n) error stop 'configuration array length'
         allocate(samples(n)); call CFG_get(config,'samples',samples)
         if (steps/=5*fixture-37 .or. dt/=real(fixture-12,real64)/8) error stop 'configuration numeric reference'
         if (.not.enabled .or. title/=expected .or. retained/=42) error stop 'configuration typed/default reference'
         if (any(samples/=[(real(i-fixture,real64)/8,i=1,n)])) error stop 'configuration array reference'
         checks=checks+5+n
         call CFG_clear(config)
      end block
   end do
   open(newunit=unit,file='config-reference.cfg',status='old'); close(unit,status='delete')
   print '(a,i0)', '24 fresh configuration/file fixtures; exact scalar and array references: ',checks
   print '(a)', 'Integer, dyadic real, logical, text, nested keys, dynamic arrays and retained defaults.'
   print '(a)', 'Valid generated inputs only; malformed files, unknown keys, repeated reads and CLI input unverified.'
   print '(a)', 'PASS config-file-reference'
end program
