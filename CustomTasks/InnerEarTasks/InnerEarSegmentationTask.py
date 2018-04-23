from AbstractTask import AbstractTask
from CustomTasks.AvailableInputs.BooleanInput import BooleanInput
from CustomTasks.AvailableInputs.PointList3D import PointList3DInput
from CustomTasks.AvailableInputs.SingleChoiceInput import SingleChoiceInput

# Example for a provided task implementation
from CustomTasks.AvailableInputs.VolumeInput import VolumeInput


class InnerEarSegmentationTask(AbstractTask):
    task_identifier = "InnerEarSegmentation"
    description = "This Service segments the inner ear within a 60x60x60 CISS volume."
    inputs = [
        VolumeInput(id="cissvolume",pretty_name="Inner ear volume",description="A 60x60x60 CISS volume for segmentation"),
        BooleanInput(id="onlyLargestComponent",pretty_name="Largest Component Filter"),
        PointList3DInput(id="center",pretty_name="Center of Inner Ear")
    ]


    def perform(self):
        import keras, os
        import numpy as np
        import SimpleITK as sitk
        import tensorflow as tf

        output_file_path = os.path.join(self.dir,"out","predicted_vol.nii.gz")
        volume = self.cleaned_values['cissvolume']
        largestComponent = self.cleaned_values['onlyLargestComponent']
        pointlist = self.cleaned_values['center']

        def dice(labels, prediction):
            dc = 2.0 * \
                 tf.reduce_sum(labels * prediction, axis=[1, 2, 3, 4]) / \
                 tf.reduce_sum(labels ** 2 + prediction ** 2, axis=[1, 2, 3, 4]) + np.finfo(np.float).eps

            return dc

        def dice_loss(labels, prediction):
            return 1.0 - dice(labels, prediction)

        def compute_dice_loss(labels, prediction):
            return tf.reduce_mean(
                dice_loss(labels=labels, prediction=prediction)
            )

        def normalize(vol):
            max_value = 1155.
            min_value = -132.
            npvol = vol.astype(dtype=float)
            normalized = (npvol - min_value) / (max_value - min_value)
            return np.clip(normalized, min_value, max_value)

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

        in_image = volume
        np_size = 40, 60, 80
        sitkSize = 80, 60, 40
        cropSpacing = np.array([0.5, 0.5, 0.5])
        cropSize = np.array(sitkSize).astype(np.float)
        direction_flip = lambda x: np.array(in_image.GetDirection()).reshape(3, 3).dot(x)

        jik_ras = np.array([-1, -1, +1])

        # determine center point / origin point
        try:
            # take last point as center point
            center_crop_point = np.array(pointlist[-1])

            box_center = 0.5 * cropSpacing * cropSize
            center_offset = jik_ras * direction_flip(box_center)
            new_origin_point = jik_ras * (center_crop_point - center_offset)

        except:
            # assume center of image
            new_origin_point = [0, 0, 0]

        resampler = sitk.ResampleImageFilter()
        resampler.SetReferenceImage(in_image)
        resampler.SetOutputSpacing(cropSpacing)
        resampler.SetSize(sitkSize)
        resampler.SetDefaultPixelValue(0)
        resampler.SetOutputDirection(in_image.GetDirection())
        resampler.SetOutputOrigin(new_origin_point)
        resampler.SetInterpolator(sitk.sitkBSpline)

        cropped_image = resampler.Execute(in_image)

        np_image = normalize(sitk.GetArrayFromImage(cropped_image))
        imgbatch = np_image.reshape(1, 40, 60, 80, 1)

        model = self.__class__.shared.get('model',None)
        if model is None:
            print("Loading model at first run... This can take some seconds.")
            model = keras.models.load_model(os.path.join(os.path.dirname(__file__),"InnerEarSegModel.hdf5"), custom_objects={'compute_dice_loss': compute_dice_loss})
            InnerEarSegmentationTask.shared['model'] = model

        np_seg = model.predict(imgbatch)

        np_seg_final = np.array(np_seg[1]).reshape(40, 60, 80)

        if largestComponent:
            print('Largest Component filter enabled')
            seg = maskLargestConnectedComponent(np_seg_final).astype(np.float)
        else:
            print('Largest Component filter disabled')
            seg = np_seg_final.astype(np.float)


        segmentation = sitk.GetImageFromArray((seg > 0.5).astype(np.float32))
        segmentation.SetOrigin(new_origin_point)
        segmentation.SetSpacing(cropSpacing)
        segmentation.SetDirection(in_image.GetDirection())

        for k in in_image.GetMetaDataKeys():
            segmentation.SetMetaData(k,in_image.GetMetaData(k))

        sitk.WriteImage(segmentation, output_file_path)

        import tarfile
        achive_output_path = os.path.join(self.dir,"out","result.tar.gz")
        with tarfile.open(achive_output_path, "w:gz") as tar:
            tar.add(output_file_path, arcname=os.path.basename(output_file_path))