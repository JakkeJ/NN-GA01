import os

import torch
from torch.utils.data import Dataset
from skimage import io

from utils import generate_phoc_vector, generate_phos_vector

import pandas as pd
import numpy as np

class phosc_dataset(Dataset):
    def __init__(self, csvfile, root_dir, transform=None, calc_phosc=True):
        self.df_all = pd.read_csv(csvfile, usecols = ["Image", "Word"])
        self.root_dir = root_dir
        self.transform = transform
        self.calc_phosc = calc_phosc

        words = self.df_all["Word"].values

        self.df_all["phos"] = [generate_phos_vector(word) for word in words]
        self.df_all["phoc"] = [np.array(generate_phoc_vector(word)) for word in words]
        self.df_all["phosc"] = [np.concatenate((generate_phos_vector(word), np.array(generate_phoc_vector(word)))) for word in words]

        self.images = [self.load_image(os.path.join(self.root_dir, image)) for image in self.df_all['Image']]

    def load_image(self, img_path):
        return io.imread(img_path)

    def __getitem__(self, index):
        image = self.images[index]

        y = torch.tensor(self.df_all.iloc[index, len(self.df_all.columns) - 1])

        if self.transform:
            image = self.transform(image)

        return image.float(), y.float(), self.df_all.iloc[index, 1]

    def __len__(self):
        return len(self.df_all)


if __name__ == '__main__':
    from torchvision.transforms import transforms

    dataset = phosc_dataset('image_data/IAM_test_unseen.csv', '../image_data/IAM_test', transform=transforms.ToTensor())

    print(dataset.df_all)

    print(dataset.__getitem__(0))
