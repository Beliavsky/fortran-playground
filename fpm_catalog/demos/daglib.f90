program main
   use dag_module, only: dag
   implicit none
   type(dag) :: graph
   integer, allocatable :: order(:)
   integer :: status
   call graph%set_vertices(3)
   call graph%set_edges(2,[1])
   call graph%set_edges(3,[2])
   call graph%toposort(order,status)
   if (status /= 0) error stop 'topological sort failed'
   if (any(order /= [1,2,3])) error stop 'incorrect dependency order'
   print *, 'Dependency order:', order
   call graph%destroy()
   print *, 'PASS daglib'
end program main
