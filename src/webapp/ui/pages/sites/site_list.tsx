import React from "react";
import {
  Box,
  Button,
  Icon,
  Stack,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { PartialSite } from "../../../casualcms/domain/model";
import { ApiError } from "../../../casualcms/domain/ports";
import { AppConfig, AppContext } from "../../../config";

import { useAuth } from "../login/hooks";
import { Link, useNavigate } from "react-router-dom";
import { AddIcon, EditIcon } from "@chakra-ui/icons";
import { Result } from "neverthrow";
import { Loader } from "../../components/loader";
import { ApiErrorUI } from "../../components/error_api";
import { SiteBreadcrumb } from "../../components/breadcrumb";
// import { SiteBreadcrumb } from "../../components/breadcrumb";

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
      <Td>{site.hostname}</Td>
      <Td>{site.root_page_path}</Td>
      <Td>{{ true: "yes", false: "no" }[site.default.toString()]}</Td>
      <Td>
        <Link
          to={`/admin/sites/edit?${new URLSearchParams({
            hostname: site.hostname,
          })}`}
        >
          <Icon as={EditIcon} marginEnd={2} />
          Edit
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
    if (token) {
      loadSubSites();
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
            <Th>Root Page</Th>
            <Th>Default</Th>
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

export const SiteListButtons: React.FunctionComponent<{}> = () => {
  let navigate = useNavigate();
  return (
    <Stack p={4} spacing={4} direction="row" align="right">
      <Button
        colorScheme="cyan"
        onClick={() => navigate(`/admin/sites/new`, { replace: true })}
      >
        <Icon as={AddIcon} marginEnd={2} />
        Add new site
      </Button>
    </Stack>
  );
};

export const SiteList: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";

  return (
    <Box>
      <SiteBreadcrumb />
      <SiteListTable config={config} token={token} />
      <SiteListButtons />
    </Box>
  );
};
