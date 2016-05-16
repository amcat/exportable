import io
import concurrent.futures
from contextlib import ContextDecorator
from queue import Queue, Empty


class QueueWriter(ContextDecorator):
    def __init__(self, queue: Queue):
        self.queue = queue

    def write(self, b):
        self.queue.put(b)


class Exporter(object):
    extension = None
    content_type = None

    def dump(self, table, fo, filename_hint=None, encoding_hint="utf-8"):
        """Write contents of a table to file like object. The only method the file like object
        needs to support is write, which should take bytes.

        @param fo: file like object
        @param filename_hint: some formats (such as zipped) need a filename
        @param encoding_hint: encoding for bytes resulting bytes. Doesn't do anything for binary
                              formats such as ODS, XLSX or SPSS.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def dumps(self, table, filename_hint=None, encoding_hint="utf-8") -> bytes:
        """Export table and return value as bytes.

        @param filename_hint: some formats (such as zipped) need a filename
        @param encoding_hint: encoding for bytes resulting bytes. Doesn't do anything for binary
                              formats such as ODS, XLSX or SPSS.
        """
        fo = io.BytesIO()
        self.dump(table, fo, filename_hint=filename_hint, encoding_hint=encoding_hint)
        return fo.getvalue()

    def _dump_iter(self, queue: Queue, table, filename_hint=None, encoding_hint="utf-8"):
        self.dump(table, QueueWriter(queue), filename_hint=filename_hint, encoding_hint=encoding_hint)

    def dump_iter(self, table, buffer_size=20, filename_hint=None, encoding_hint="utf-8") -> [bytes]:
        """Export table and return an iterator of bytes. This is particularly useful for Django,
        which supports streaming responses through iterators.

        @param buffer_size: store up to N write() message in buffer
        @param filename_hint: some formats (such as zipped) need a filename
        @param encoding_hint: encoding for bytes resulting bytes. Doesn't do anything for binary
                              formats such as ODS, XLSX or SPSS.
        """
        queue = Queue(maxsize=buffer_size)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._dump_iter, queue, table, filename_hint, encoding_hint)

            while future.running() or not queue.empty():
                try:
                    # Make sure to quit if the thread threw an error
                    yield queue.get(timeout=0.2)
                except Empty:
                    continue

            # If any exceptions occurred while running _dump_iter, the exception will be thrown
            future.result()

    def dump_http_reponse(self, table, filename=None, encoding_hint="utf-8"):
        """Render table as a Django response.

        @param filename: filename to suggest to browser
        @param filename_hint: some formats (such as zipped) need a filename
        @param encoding_hint: encoding for bytes resulting bytes. Doesn't do anything for binary
                              formats such as ODS, XLSX or SPSS.
        @return: Django streaming HTTP response
        """
        from django.http.response import StreamingHttpResponse
        content = self.dump_iter(table, encoding_hint=encoding_hint, filename_hint=filename)
        response = StreamingHttpResponse(content, content_type=self.content_type)
        if filename:
            attachment = 'attachment; filename="{}.{}"'.format(filename, self.extension)
            response['Content-Disposition'] = attachment
        return response
