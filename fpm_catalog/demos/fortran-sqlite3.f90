program main
   use iso_c_binding, only: c_ptr, c_null_funptr, c_null_ptr
   use sqlite3
   implicit none
   type(c_ptr) :: db, statement
   character(:), allocatable :: message
   integer :: rc, count
   real(kind(1.d0)) :: average
   rc=sqlite3_open(':memory:',db)
   if (rc /= SQLITE_OK) error stop 'cannot open database'
   rc=sqlite3_exec(db,'CREATE TABLE observations(value REAL);'// &
      'INSERT INTO observations VALUES(1.0),(2.0),(3.0),(4.0),(5.0);', &
      c_null_funptr,c_null_ptr,message)
   if (rc /= SQLITE_OK) error stop 'cannot create observations'
   rc=sqlite3_prepare_v2(db,'SELECT COUNT(*), AVG(value) FROM observations',statement)
   if (rc /= SQLITE_OK) error stop 'cannot prepare query'
   rc=sqlite3_step(statement)
   if (rc /= SQLITE_ROW) error stop 'missing query result'
   count=sqlite3_column_int(statement,0)
   average=sqlite3_column_double(statement,1)
   if (count /= 5 .or. abs(average-3.d0)>1.d-12) error stop 'incorrect query result'
   print *, 'Observation count and average:',count,average
   rc=sqlite3_step(statement)
   if (rc /= SQLITE_DONE) error stop 'unexpected additional row'
   rc=sqlite3_finalize(statement)
   if (rc /= SQLITE_OK) error stop 'cannot finalize query'
   rc=sqlite3_close(db)
   if (rc /= SQLITE_OK) error stop 'cannot close database'
   print *, 'PASS fortran-sqlite3'
end program main
