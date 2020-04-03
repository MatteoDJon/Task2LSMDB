import matplotlib.pyplot as plt
import numpy as np


def histogramAverageMonth( x_axis, label):
    print("TODO")
    labels = label
    men_means = x_axis
    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, men_means, width, label='Average\nvote')

    ax.set_ylabel('Averages vote per month')
    ax.set_xlabel('Months')

    ax.set_title('Average votes per month')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    fig.tight_layout()
    plt.show()

if __name__ == '__main__':
    x_axis=["ott", "nov", "dec"]
    label=[4, 354, 6]
    histogramAverageMonth(label, x_axis)