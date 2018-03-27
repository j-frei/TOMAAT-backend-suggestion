from AbstractTask import AbstractTask
from CustomTasks.AvailableInputs.SingleChoiceInput import SingleChoiceInput

# Example for a provided task implementation
from CustomTasks.AvailableInputs.VolumeInput import VolumeInput


class InnerEarSegmentationTask(AbstractTask):
    task_identifier = "InnerEarSegmentation"
    description = "This Service segments the inner ear within a 60x60x60 CISS volume."
    inputs = [
        VolumeInput(id="cissvolume",pretty_name="Inner ear volume",description="A 60x60x60 CISS volume for segmentation")
    ]


    def perform(self):
        import keras, os
        import numpy as np
        import SimpleITK as sitk
        import tensorflow as tf
        output_file_path = os.path.join(self.dir,"out","predicted_vol.nii.gz")
        volume = self.cleaned_values['cissvolume']

        # COPY AND PASTE FROM SCRIPT

        def getCenteredOrigin(img):
            return np.array(img.GetDirection()).reshape(3, 3).dot(np.array([-0.5, -0.5, -0.5])) * np.array(
                img.GetSize()) * np.array(img.GetSpacing())

        def dice(labels, prediction):
            dc = 2.0 * \
                 tf.reduce_sum(labels * prediction, axis=[1, 2, 3, 4]) / \
                 tf.reduce_sum(labels ** 2 + prediction ** 2, axis=[1, 2, 3, 4]) + np.finfo(float).eps

            return dc

        def dice_loss(labels, prediction):
            return 1.0 - dice(labels, prediction)

        def compute_dice_loss(labels, prediction):
            return tf.reduce_mean(
                dice_loss(labels=labels, prediction=prediction)
            )

        def maskLargestConnectedComponent(image_np):
            image = sitk.GetImageFromArray(image_np)
            f = sitk.BinaryThresholdImageFilter()
            # define threshold to be at half beween min and max
            f.SetLowerThreshold(image_np.min() + 0.5 * (image_np.max() - image_np.min()))
            # set upper threshold to exceed max image value
            f.SetUpperThreshold(image_np.max() + 10.0)
            i_bin = f.Execute(image)
            # find connected components
            labeled_i = sitk.ConnectedComponent(i_bin)
            # convert to numpy array
            l_i_np = sitk.GetArrayFromImage(labeled_i)
            # return map with largest connected component
            return l_i_np == np.argsort(np.bincount(l_i_np.ravel()))[-2]

        m = keras.models.load_model(os.path.join(os.path.dirname(__file__),"InnerEarSegModel.pkl"), custom_objects={'compute_dice_loss': compute_dice_loss})
        np_image = sitk.GetArrayFromImage(volume).astype(dtype=float)
        np_seg = m.predict(np_image.reshape(1, 60, 60, 60, 1))
        np_seg_final = np.array(np_seg[1]).reshape(60, 60, 60)

        seg = sitk.GetImageFromArray(maskLargestConnectedComponent(np_seg_final).astype(float))

        # copy metadata/properties
        seg.SetSpacing(volume.GetSpacing())
        for k in volume.GetMetaDataKeys():
            seg.SetMetaData(k, volume.GetMetaData(k))
        # center image
        seg.SetOrigin(volume.GetOrigin())
        seg.SetDirection(volume.GetDirection())

        sitk.WriteImage(seg, output_file_path)
        # END OF COPY AND PASTE FROM SCRIPT

        import tarfile
        achive_output_path = os.path.join(self.dir,"out","result.tar.gz")
        with tarfile.open(achive_output_path, "w:gz") as tar:
            tar.add(output_file_path, arcname=os.path.basename(output_file_path))