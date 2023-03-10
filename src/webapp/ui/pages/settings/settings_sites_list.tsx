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
import { PartialSite } from "../../../casualcms/domain/model";
import { ApiError } from "../../../casualcms/domain/ports";
import { AppConfig, useConfig } from "../../../config";
import { SettingBreadcrumb } from "../../components/breadcrumb";
import { ApiErrorUI } from "../../components/error_api";
import { Loader } from "../../components/loader";
import { useAuth } from "../login/hooks";

type SettingSiteRowProps = {
  site: PartialSite;
};

type SettingSiteListTableProps = {
  config: AppConfig;
  token: string;
};

export const SettingSiteRow: React.FunctionComponent<SettingSiteRowProps> = (
  props: SettingSiteRowProps,
) => {
  const site = props.site;
  return (
    <Tr>
      <Td>
        <Link to={`/admin/settings/${site.hostname}`}>{site.hostname}</Link>
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

export const SettingSiteListTable: React.FunctionComponent<SettingSiteListTableProps> =
  (props: SettingSiteListTableProps) => {
    const config = props.config;
    const token = props.token;
    const [isLoading, setIsLoading] = React.useState<boolean>(true);
    const [sites, setSites] = React.useState<PartialSite[]>([]);
    const [error, setError] = React.useState<ApiError>(null);

    React.useEffect(() => {
      async function loadSites() {
        let sites: Result<PartialSite[], ApiError>;
        sites = await config.api.site.listSites(token);
        sites
          .map((sites: PartialSite[]) => setSites(sites))
          .mapErr((err: ApiError) => setError(err)); // FIXME
        setIsLoading(false);
      }
      if (token) {
        loadSites();
      }
      return function cleanup() {};
    }, [token]);

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
            {sites.map((site) => (
              <SettingSiteRow site={site} key={site.hostname} />
            ))}
          </Tbody>
        </Table>
      </TableContainer>
    );
  };

export const SettingSiteList: React.FunctionComponent<{}> = () => {
  const config = useConfig();
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";

  return (
    <Box minW="1440px">
      <SettingBreadcrumb />
      <Box maxW="1440px">
        <SettingSiteListTable config={config} token={token} />
      </Box>
    </Box>
  );
};
