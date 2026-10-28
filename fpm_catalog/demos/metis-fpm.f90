program demo_metis
   use iso_c_binding, only: c_int
   use metis_c_interface
   implicit none
   integer(idx_t) :: xadj(10), adjncy(24), weights(24), options(0:METIS_NOPTIONS-1)
   integer(idx_t) :: part(9), edgecut, nvtxs, ncon, nparts
   integer(c_int) :: status
   integer :: row, col, vertex, next, other, cuts, i

   ! Undirected 3-by-3 grid graph, with zero-based vertex numbers for METIS.
   next = 1
   do row = 0, 2
      do col = 0, 2
         vertex = 3*row + col
         xadj(vertex+1) = int(next-1, idx_t)
         if (row > 0) then
            adjncy(next) = int(vertex-3, idx_t); next = next+1
         end if
         if (row < 2) then
            adjncy(next) = int(vertex+3, idx_t); next = next+1
         end if
         if (col > 0) then
            adjncy(next) = int(vertex-1, idx_t); next = next+1
         end if
         if (col < 2) then
            adjncy(next) = int(vertex+1, idx_t); next = next+1
         end if
      end do
   end do
   xadj(10) = int(next-1, idx_t)
   weights = 1_idx_t
   nvtxs = 9_idx_t; ncon = 1_idx_t; nparts = 2_idx_t
   status = METIS_SetDefaultOptions(options)
   if (status /= METIS_OK) error stop 'METIS default options failed'
   options(METIS_OPTION_SEED) = 42_idx_t
   status = METIS_PartGraphRecursive(nvtxs, ncon, xadj, adjncy, adjwgt=weights, &
      nparts=nparts, options=options, edgecut=edgecut, part=part)
   if (status /= METIS_OK) error stop 'METIS partition failed'
   if (any(part < 0_idx_t) .or. any(part >= nparts)) error stop 'Invalid partition'
   if (count(part == 0) < 3 .or. count(part == 1) < 3) error stop 'Unbalanced partition'
   cuts = 0
   do vertex = 1, 9
      do i = int(xadj(vertex))+1, int(xadj(vertex+1))
         other = int(adjncy(i))+1
         if (part(vertex) /= part(other)) cuts = cuts+1
      end do
   end do
   if (cuts/2 /= edgecut) error stop 'Edge cut check failed'
   print '(a,2i4)', 'Partition sizes:', count(part == 0), count(part == 1)
   print '(a,i4)', 'Edges crossing partitions:', edgecut
   do row = 0, 2
      print '(3i4)', part(3*row+1:3*row+3)
   end do
   print *, 'PASS metis-fpm'
end program demo_metis
