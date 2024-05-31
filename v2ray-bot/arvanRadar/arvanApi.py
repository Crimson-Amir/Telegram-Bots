import asyncio
import aiohttp


class SessionError(Exception):
    def __init__(self, message=None):
        super().__init__(message)

class ArvanRequest:
    def __init__(self, session):
        self._session = session
        print('session set success!')


    async def make_request(self, url):
        if not self._session:
            raise SessionError("seesion is not set!")

        try:
            async with self._session.get(url) as response:
                if hasattr(response, 'json'):
                    return await response.json()

        except aiohttp.ClientConnectorError:
            return None


class ArvanRequestFactory:
    @staticmethod
    async def run_requests(requests_list):

        async with aiohttp.ClientSession() as session:
            arvan_request = ArvanRequest(session)
            requests = [arvan_request.make_request(request) for request in requests_list]
            resluts = await asyncio.gather(*requests, return_exceptions=True)
            return resluts

    def get_requests(self, requests_list: list):
        return asyncio.run(self.run_requests(requests_list))


class ArvanRadar:
    def __init__(self, datacenter_keys, url_format):
        self.request_address_list = datacenter_keys
        self._url_format = url_format

    def set_request_address_list(self, address_list):
        self.request_address_list = address_list

    def create_address_list(self, *site_name):
        list_of_url = [self.request_address_list[url] for url in site_name]
        return [self._url_format.format(key) for key in list_of_url]

    def get_data(self, *site_name):
        """
        :param site_name: name of datacenters. check ./extraData.datacenter_keys
        :return: data from 6 hours ago
        """
        addresses = self.create_address_list(*site_name)
        request_manager = ArvanRequestFactory()
        return list(zip(site_name, request_manager.get_requests(addresses)))

    def set_time(self, date, time):
        self._url_format = self._url_format + f'&date={date}&time={time}'


class OptimizeProxy:
    @staticmethod
    def homogenization(data):
        site_values = []
        for site in data:
            site_values.extend([list(val[:360] for val in site[1].values())])
        return site_values

    def average_platforms(self, data):
        homogenization_data = self.homogenization(data)
        ziped_data = [list(zip(*values)) for values in homogenization_data]
        return [[round(sum(group) / len(group), 2) for group in ziped] for ziped in ziped_data]



# a = ArvanRadar()
# b = a.get_data('Hamrah_aval', 'Irancell', 'Mobin_net', 'Afranet', 'Pars_online', 'Host_iran', 'Tehran_1', 'Tehran_2')
# print(OptimizeProxy().average_platforms(b))
# p = RadarPlot(b)
# a = p.make_plot_2()
