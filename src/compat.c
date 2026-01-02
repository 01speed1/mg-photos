#include <stdlib.h>
#include <errno.h>

// Android API 15 tiene memalign en <malloc.h>, lo declaramos manualmente
extern void *memalign(size_t alignment, size_t size);

int posix_memalign(void **memptr, size_t alignment, size_t size)
{
  if (alignment < sizeof(void *))
    alignment = sizeof(void *);
  void *ptr = memalign(alignment, size);
  if (!ptr)
    return 12; // ENOMEM
  *memptr = ptr;
  return 0;
}

int dl_iterate_phdr(int (*callback)(void *, size_t, void *), void *data)
{
  (void)callback;
  (void)data;
  return 0;
}

typedef void (*sighandler_t)(int);
extern sighandler_t bsd_signal(int, sighandler_t);
sighandler_t signal(int s, sighandler_t f)
{
  return bsd_signal(s, f);
}

unsigned long getauxval(unsigned long type)
{
  (void)type;
  return 0;
}