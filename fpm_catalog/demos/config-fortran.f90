program main
   use iso_fortran_env, only: real64
   use m_config, only: CFG_t, CFG_add, CFG_get, CFG_get_size, CFG_read_file, CFG_clear
   implicit none
   type(CFG_t) :: config
   integer :: unit, steps, n
   real(real64) :: dt
   real(real64), allocatable :: values(:)
   logical :: enabled
   character(40) :: title

   call CFG_add(config, 'steps', 10, 'Number of time steps')
   call CFG_add(config, 'solver%dt', 0.1_real64, 'Time step')
   call CFG_add(config, 'enabled', .false., 'Enable calculation')
   call CFG_add(config, 'title', 'default', 'Run title')
   call CFG_add(config, 'samples', [0.0_real64], 'Sample values', dynamic_size=.true.)
   ! Create the entire small input file so this example is self-contained.
   open(newunit=unit, file='settings.cfg', status='replace', action='write')
   write(unit, '(a)') 'steps = 25', 'solver%dt = 0.025', 'enabled = .true.', &
      'title = playground', 'samples = 1.0 2.0 4.0'
   close(unit)
   call CFG_read_file(config, 'settings.cfg')
   call CFG_get(config, 'steps', steps)
   call CFG_get(config, 'solver%dt', dt)
   call CFG_get(config, 'enabled', enabled)
   call CFG_get(config, 'title', title)
   call CFG_get_size(config, 'samples', n)
   allocate(values(n))
   call CFG_get(config, 'samples', values)
   if (steps /= 25 .or. .not. enabled) error stop 'scalar settings'
   if (abs(dt-0.025_real64) > 1.0e-14_real64) error stop 'time step'
   if (trim(title) /= 'playground') error stop 'title'
   if (n /= 3) error stop 'dynamic array size'
   if (maxval(abs(values-[1.0_real64,2.0_real64,4.0_real64])) > 1.0e-14_real64) error stop 'array'
   print '(a)', 'Title: '//trim(title)
   print '(a,i0)', 'Steps: ', steps
   print '(a,f7.3)', 'Time step: ', dt
   print '(a,3f6.1)', 'Samples: ', values
   call CFG_clear(config)
   print '(a)', 'PASS config-fortran'
end program main
