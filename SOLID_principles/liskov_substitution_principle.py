class BaseFileUploader:
    """
    Objects of a superclass should be able to be replaced with
    objects of any of its subclasses without breaking the correctness of the program.
    It usually follows the OCP principle method.
    And also it is achieved mostly using Inheritance guidelines.
    """
    def upload_file(self, filename):
        # generic file upload code
        raise NotImplementedError


class ImageUploader(BaseFileUploader):
    def upload_file(self, filename):
        # image upload code
        print(f"Uploading image {filename} to server...")


class VideoUploader(BaseFileUploader):
    def upload_file(self, filename):
        # video upload code
        print(f"Uploading video {filename} to server...")


class DocumentUploader(BaseFileUploader):
    def upload_file(self, filename):
        # document upload code
        print(f"Uploading document {filename} to server...")


image_uploader = ImageUploader()
video_uploader = VideoUploader()
document_uploader = DocumentUploader()


def upload_to_server(file_uploader, filename):
    file_uploader.upload_file(filename)


upload_to_server(image_uploader, "image.jpg")
upload_to_server(video_uploader, "video.mp4")
upload_to_server(document_uploader, "document.pdf")


###########################################################
#          Class violation of LSP example                 #
###########################################################
# We can treat the objects of subclass as objects of super class.This is because the subclass objects implements the same
# interface as the superclass, and the function(upload_to_server) does not rely on the specific implementation details of the subclass.

# In the given code, the DocumentUploader class violates LSP because it raises a TypeError exception for files that do
# not end with ".pdf". This behavior is not expected from its base class BaseFileUploader, which does not have any such
# restriction. Therefore, if we replace an object of the BaseFileUploader class with an object of the DocumentUploader class,
# the behavior of the program changes, and it may lead to errors or unexpected results.


class BaseFileUploader:
    def upload_file(self, filename):
        # generic file upload code
        raise NotImplementedError


class ImageUploader(BaseFileUploader):
    def upload_file(self, filename):
        # image upload code
        print(f"Uploading image {filename} to server...")


class VideoUploader(BaseFileUploader):
    def upload_file(self, filename):
        # video upload code
        print(f"Uploading video {filename} to server...")


class DocumentUploader(BaseFileUploader):
    def upload_file(self, filename):
        if not filename.endswith('.pdf'):
            raise TypeError("Invalid file type")  # this line violates LSP
        # document upload code
        print(f"Uploading document {filename} to server...")


image_uploader = ImageUploader()
video_uploader = VideoUploader()
document_uploader = DocumentUploader()


def upload_to_server(file_uploader, filename):
    file_uploader.upload_file(filename)


upload_to_server(image_uploader, "image.jpg")
upload_to_server(video_uploader, "video.mp4")
upload_to_server(document_uploader, "document.pdf")
upload_to_server(document_uploader, "document.docx")  # this call violates LSP
