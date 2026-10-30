! A small configuration is created locally; no external data file is needed.
program main
   use yafyaml
   implicit none
   type(Parser) :: reader
   class(YAML_Node), allocatable :: document
   integer, allocatable :: samples(:)
   integer :: unit, rc, iterations
   logical :: enabled
   character(:), allocatable :: title
   open(newunit=unit, file='settings.yaml', status='replace', action='write')
   write(unit,'(a)') 'title: Fortran playground', 'iterations: 12', 'enabled: true', &
      'samples: [2, 3, 5, 7]', 'solver:', '  tolerance: 0.001'
   close(unit)
   reader = Parser('core')
   document = reader%load('settings.yaml')
   call document%get(iterations, 'iterations', rc=rc)
   if (rc /= YAFYAML_SUCCESS .or. iterations /= 12) error stop 'Integer setting mismatch'
   call document%get(enabled, 'enabled', rc=rc)
   if (rc /= YAFYAML_SUCCESS .or. .not. enabled) error stop 'Boolean setting mismatch'
   call document%get(title, 'title', rc=rc)
   if (rc /= YAFYAML_SUCCESS) error stop 'String setting failed'
   if (title /= 'Fortran playground') error stop 'String setting mismatch'
   call document%get(samples, 'samples', rc=rc)
   if (rc /= YAFYAML_SUCCESS) error stop 'Sequence setting failed'
   if (size(samples) /= 4) error stop 'Sequence size mismatch'
   if (any(samples /= [2,3,5,7])) error stop 'Sequence values mismatch'
   if (document%has('missing')) error stop 'Unexpected missing key'
   print '(a)', 'Title: '//title
   print '(a,i0)', 'Iterations: ', iterations
   print '(a,l1)', 'Enabled: ', enabled
   print '(a,4i4)', 'Samples: ', samples
   open(newunit=unit, file='settings.yaml', status='old')
   close(unit, status='delete')
   print '(a)', 'PASS yafyaml'
end program main
