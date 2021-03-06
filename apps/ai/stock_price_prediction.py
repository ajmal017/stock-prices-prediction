from libs.stocks.get_stock_info import GetStocksInfo
from libs.signal_generator.get_signal_info import GetSignalInfo
from libs.dataset.perceptron.load_dataset import *
from libs.dl_models.dl_models import DLModels
from libs.callback.callback import CallBack
import apps.ai.config as config
from tqdm import tqdm
import threading

prediction_type = config.prediction_type
window_size = config.window_size
stock_names = config.signal_names if config.TEST else config.stock_names

stocks_obj = GetSignalInfo() if config.TEST else GetStocksInfo()
dl_models_obj = DLModels(prediction_type=config.prediction_type)
callback = CallBack()


def measuer(): stocks_obj.measure()


x = threading.Thread(target=measuer)
x.start()

for i in tqdm(range(config.window_size + 10 ** 3)):
    for time_scale_index, time_scale in enumerate(config.time_scales):

        # todo: this only works for MANY2ONE becuse of config.signal_name[0]
        stock_monitor = stocks_obj.stocks[stock_names[0]]['stock_obj'].time_scales[time_scale]  # Queue

        trainX_s, trainY_s, testX_s, testY_s = None, None, None, None

        for stock_name in stock_names:
            batch = stocks_obj.stocks[stock_name]['stock_obj'].time_scales[time_scale]  # Queue or Candle

            trainX, trainY, testX, testY = pre_process(batch, int(config.max_window_size[time_scale] * 0.5))

            trainX_s, testX_s, trainY_s, testY_s = stack_dataset(trainX_s, testX_s, trainY_s, testY_s, trainX, testX,
                                                                 trainY, testY, time_scale)

        # reshape
        trainX_s = trainX_s[np.newaxis, :, :]
        testX_s = testX_s[np.newaxis, :, :]
        trainY_s = trainY_s[np.newaxis, :]
        testY_s = testY_s[np.newaxis, :]

        dl_models_obj.fit(trainX=trainX_s, trainY=trainY_s, testX=testX_s, testY=testY_s, callback=callback,
                          time_scale_index=time_scale_index, time_scale=time_scale, stock_monitor=stock_monitor, i=i)

# dl_models_obj.save()
