import { EditIcon } from "@chakra-ui/icons";
import {
  Box,
  Icon,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { Result } from "neverthrow";
import React from "react";
import { Link } from "react-router-dom";
import { PartialSite } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppConfig, AppContext } from "../../config";
import { ApiErrorUI } from "../layout/error_api";
import { Loader } from "../layout/loader";
import { useAuth } from "../login/hooks";

type SiteRowProps = {
  site: PartialSite;
};

type SiteListTableProps = {
  config: AppConfig;
  token: string;
};

export const SiteRow: React.FunctionComponent<SiteRowProps> = (
  props: SiteRowProps
) => {
  const site = props.site;
  return (
    <Tr>
      <Td>
        <Link to={`/admin/settings/${site.hostname}`}>
          {site.hostname}
        </Link>
      </Td>
      <Td>
        <Link to={`/admin/settings/${site.hostname}`}>
          <Icon as={EditIcon} marginEnd={2} />
          Edit Settings
        </Link>
      </Td>
    </Tr>
  );
};

export const SiteListTable: React.FunctionComponent<SiteListTableProps> = (
  props: SiteListTableProps
) => {
  const config = props.config;
  const token = props.token;
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [sites, setSites] = React.useState<PartialSite[]>([]);
  const [error, setError] = React.useState<ApiError>(null);

  React.useEffect(() => {
    async function loadSubSites() {
      let sites: Result<PartialSite[], ApiError>;
      sites = await config.api.site.listSites(token);
      sites
        .map((sites: PartialSite[]) => setSites(sites))
        .mapErr((err: ApiError) => setError(err)); // FIXME
      setIsLoading(false);
    }
    loadSubSites();
    return function cleanup() {};
  }, []);

  if (isLoading) {
    return <Loader label="Loading sites list" />;
  }
  if (error) {
    return <ApiErrorUI error={error} />;
  }
  return (
    <TableContainer>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Hostname</Th>
            <Th>Edit</Th>
          </Tr>
        </Thead>
        <Tbody>
          {sites.map((site, i) => (
            <SiteRow site={site} key={i} />
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
};

export const SettingSiteList: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";

  return (
    <Box>
      <SiteListTable config={config} token={token} />
    </Box>
  );
};
